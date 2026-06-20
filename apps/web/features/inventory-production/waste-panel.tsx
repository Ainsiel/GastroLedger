"use client";
import type { ApiProblem, WasteResponse, WasteSubmissionRequest } from "@gastroledger/api-contract";
import { Trash2 } from "lucide-react";
import { FormEvent, useState } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function WastePanel() {
  const [result,setResult]=useState<WasteResponse|null>(null); const [error,setError]=useState<string|null>(null); const [pending,setPending]=useState(false);
  async function send(path:string, body:object) { setPending(true); setError(null); const response=await fetch(path,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body)}); if(response.ok)setResult(await response.json() as WasteResponse); else {const problem=await response.json() as ApiProblem; setError(`Waste was not updated. Reference: ${problem.correlationId}`);} setPending(false); }
  async function submit(event:FormEvent<HTMLFormElement>){event.preventDefault();const form=new FormData(event.currentTarget);const command=String(form.get("commandId"));const body:WasteSubmissionRequest={warehouseId:String(form.get("warehouseId")),lotId:String(form.get("lotId")),quantity:String(form.get("quantity")),reason:String(form.get("reason"))};await send(`/api/v1/inventory/waste/commands/${command}`,body);}
  async function decide(event:FormEvent<HTMLFormElement>){event.preventDefault();const form=new FormData(event.currentTarget);const button=(event.nativeEvent as SubmitEvent).submitter as HTMLButtonElement;const action=button.value;const id=String(form.get("wasteId"));const command=String(form.get("decisionCommandId"));const reason=String(form.get("decisionReason"));const path=action==="reject"?`/api/v1/inventory/waste/${id}/reject`:`/api/v1/inventory/waste/${id}/${action}/${command}`;await send(path,{reason});}
  return <Card className="min-w-0 overflow-hidden"><CardHeader><div className="flex items-center gap-2"><Trash2 className="size-5 text-primary" aria-hidden="true"/><CardTitle>Operational waste</CardTitle></div><CardDescription>Record lot waste with approval evidence and immutable corrections.</CardDescription></CardHeader><CardContent className="space-y-6">
    {error?<Alert role="alert" className="border-red-200 bg-red-50"><AlertTitle>Waste not updated</AlertTitle><AlertDescription>{error}</AlertDescription></Alert>:null}
    {result?<Alert role="status" className="border-emerald-200 bg-emerald-50"><AlertTitle>Waste {result.status}</AlertTitle><AlertDescription>{result.quantity} units, operational value {result.operationalValue}.</AlertDescription></Alert>:null}
    <form onSubmit={submit} className="grid gap-4 md:grid-cols-2 xl:grid-cols-4"><Field id="waste-command" label="Waste command key" name="commandId" required/><Field id="waste-warehouse" label="Waste warehouse ID" name="warehouseId" required/><Field id="waste-lot" label="Waste lot ID" name="lotId" required/><Field id="waste-quantity" label="Waste quantity" name="quantity" required/><Field id="waste-reason" label="Waste reason" name="reason" required/><Button type="submit" disabled={pending}>Submit waste</Button></form>
    <form onSubmit={decide} className="grid gap-4 md:grid-cols-2 xl:grid-cols-4"><Field id="waste-id" label="Waste record ID" name="wasteId" required/><Field id="decision-command" label="Decision command key" name="decisionCommandId"/><Field id="decision-reason" label="Decision or correction reason" name="decisionReason"/><div className="flex flex-wrap gap-2 xl:col-span-4"><Button name="action" value="approve" variant="outline" disabled={pending}>Approve waste</Button><Button name="action" value="reject" variant="outline" disabled={pending}>Reject waste</Button><Button name="action" value="correct" disabled={pending}>Correct waste</Button></div></form>
  </CardContent></Card>;
}
function Field({id,label,name,...props}:{id:string;label:string;name:string}&React.ComponentProps<typeof Input>){return <div className="space-y-2"><Label htmlFor={id}>{label}</Label><Input id={id} name={name} {...props}/></div>;}
