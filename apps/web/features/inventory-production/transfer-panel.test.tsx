// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { TransferPanel } from "./transfer-panel";

describe("stock transfer lifecycle", () => {
  afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
  it("requests a transfer and announces pending state", async () => {
    const user = userEvent.setup(); vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json({
      transferId:"t1",transferNumber:"TR-001",status:"requested",sourceWarehouseId:"s",destinationWarehouseId:"d",itemType:"ingredient",itemId:"i",unitId:"u",requestedQuantity:"5",approvedQuantity:"0",dispatchedQuantity:"0",receivedQuantity:"0",lossQuantity:"0"
    })));
    render(<TransferPanel />);
    for (const [label,value] of [[/transfer number/i,"TR-001"],[/source warehouse id/i,"s"],[/destination warehouse id/i,"d"],[/stock item id/i,"i"],[/transfer unit id/i,"u"],[/requested quantity/i,"5"]] as const) await user.type(screen.getByLabelText(label), value);
    await user.click(screen.getByRole("button", {name:/request transfer/i}));
    expect(await screen.findByText(/Transfer TR-001: requested/i)).toBeTruthy();
  });
  it("preserves action input on conflict", async () => {
    const user = userEvent.setup(); vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json({type:"inventory.transfer_conflict",title:"failed",status:409,correlationId:"conflict-1",errors:[]},{status:409})));
    render(<TransferPanel />); await user.type(screen.getByLabelText(/^Transfer ID$/i), "t1"); await user.type(screen.getByLabelText(/command key/i), "receive-1"); await user.type(screen.getByLabelText(/action quantity/i), "5");
    await user.click(screen.getByRole("button", {name:/receive transfer/i}));
    expect((await screen.findByRole("alert")).textContent).toMatch(/conflict-1/); expect((screen.getByLabelText(/^Transfer ID$/i) as HTMLInputElement).value).toBe("t1");
  });
});
