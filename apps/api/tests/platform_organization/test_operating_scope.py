from gastroledger_api.modules.platform_organization.public import (
    CreateBranch,
    CreateWarehouse,
    DeactivateWarehouse,
    OperatingAuthorizationDenied,
    OperatingIdentity,
    OperatingScopeService,
    OperatingValidationError,
    UpdateTenantSettings,
    WarehouseDeactivationUnsafe,
    validate_branch,
    validate_tenant_settings,
    validate_warehouse,
)


def test_valid_tenant_settings_are_normalized_and_bounded() -> None:
    settings = validate_tenant_settings(
        locale=" ES ",
        base_currency=" clp ",
        branch_limit=4,
    )

    assert settings.locale == "es"
    assert settings.base_currency == "CLP"
    assert settings.branch_limit == 4


def test_unsupported_currency_and_non_integer_limit_are_rejected() -> None:
    try:
        validate_tenant_settings(
            locale="es",
            base_currency="BTC",
            branch_limit=True,
        )
    except OperatingValidationError as error:
        assert {(detail.field, detail.code) for detail in error.details} == {
            ("baseCurrency", "unsupported"),
            ("branchLimit", "invalid_integer"),
        }
    else:
        raise AssertionError("unsupported settings must fail")


def test_branch_and_warehouse_inputs_normalize_scoped_codes() -> None:
    branch = validate_branch(name="  Downtown  ", code=" main-01 ")
    warehouse = validate_warehouse(
        name="  Main Kitchen  ",
        code=" kitchen-01 ",
        warehouse_type="KITCHEN",
    )

    assert (branch.name, branch.code) == ("Downtown", "MAIN-01")
    assert (warehouse.name, warehouse.code, warehouse.warehouse_type) == (
        "Main Kitchen",
        "KITCHEN-01",
        "kitchen",
    )


class RecordingOperatingStore:
    def __init__(self) -> None:
        self.updated = False
        self.branch = None
        self.warehouse = None
        self.deactivated_warehouse_id = None

    def update_settings(self, *_args: object, **_kwargs: object) -> None:
        self.updated = True

    def create_branch(self, _identity: object, branch: object, _correlation_id: str) -> object:
        self.branch = branch
        return branch

    def create_warehouse(
        self,
        _identity: object,
        branch_id: str,
        warehouse: object,
        _correlation_id: str,
    ) -> object:
        self.warehouse = (branch_id, warehouse)
        return warehouse

    def deactivate_warehouse(
        self,
        _identity: object,
        warehouse_id: str,
        _correlation_id: str,
    ) -> object:
        self.deactivated_warehouse_id = warehouse_id
        return warehouse_id


class RecordingMovementGuard:
    def __init__(self, *, open_movements: bool = False) -> None:
        self.open_movements = open_movements

    def has_open_movements(self, _identity: object, _warehouse_id: str) -> bool:
        return self.open_movements


def test_non_admin_cannot_update_tenant_settings() -> None:
    store = RecordingOperatingStore()
    service = OperatingScopeService(store=store, movement_guard=RecordingMovementGuard())

    try:
        service.update_settings(
            OperatingIdentity(tenant_id="tenant-1", actor_id="actor-1", role="operator"),
            UpdateTenantSettings(locale="es", base_currency="CLP", branch_limit=2),
            correlation_id="correlation-1",
        )
    except OperatingAuthorizationDenied:
        pass
    else:
        raise AssertionError("non-admin settings update must be forbidden")

    assert not store.updated


def test_tenant_admin_creates_a_normalized_branch_through_the_store_policy() -> None:
    store = RecordingOperatingStore()
    service = OperatingScopeService(store=store, movement_guard=RecordingMovementGuard())

    branch = service.create_branch(
        OperatingIdentity(tenant_id="tenant-1", actor_id="actor-1", role="tenant_admin"),
        CreateBranch(name="  Downtown  ", code=" main "),
        correlation_id="correlation-1",
    )

    assert branch is store.branch
    assert getattr(store.branch, "name") == "Downtown"
    assert getattr(store.branch, "code") == "MAIN"


def test_tenant_admin_creates_and_deactivates_a_warehouse_through_store_policy() -> None:
    store = RecordingOperatingStore()
    service = OperatingScopeService(store=store, movement_guard=RecordingMovementGuard())
    identity = OperatingIdentity(
        tenant_id="tenant-1",
        actor_id="actor-1",
        role="tenant_admin",
    )

    warehouse = service.create_warehouse(
        identity,
        CreateWarehouse(
            branch_id="branch-1",
            name="  Main Bar  ",
            code=" bar-01 ",
            warehouse_type="BAR",
        ),
        correlation_id="correlation-1",
    )
    deactivated = service.deactivate_warehouse(
        identity,
        DeactivateWarehouse(warehouse_id="warehouse-1"),
        correlation_id="correlation-2",
    )

    assert warehouse is store.warehouse[1]
    assert getattr(warehouse, "code") == "BAR-01"
    assert getattr(warehouse, "warehouse_type") == "bar"
    assert deactivated == "warehouse-1"
    assert store.deactivated_warehouse_id == "warehouse-1"


def test_open_warehouse_movements_block_deactivation_before_store_mutation() -> None:
    store = RecordingOperatingStore()
    service = OperatingScopeService(
        store=store, movement_guard=RecordingMovementGuard(open_movements=True)
    )

    try:
        service.deactivate_warehouse(
            OperatingIdentity(
                tenant_id="tenant-1", actor_id="actor-1", role="tenant_admin"
            ),
            DeactivateWarehouse(warehouse_id="warehouse-1"),
            correlation_id="correlation-1",
        )
    except WarehouseDeactivationUnsafe:
        pass
    else:
        raise AssertionError("open movements must block warehouse deactivation")

    assert store.deactivated_warehouse_id is None
