const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export type PlannerType = 'interior'|'event'|'jewelry';
export type Item = {name:string; quantity:number; price?:number; priceSource?:'verified'|'illustrative'};
export type Category = {name:string; items:Item[]};
export type PlanData = {budget:number; categories:Category[]; preferences:Record<string,string>};
export type Calculation = {budget:number;estimatedTotal:number;verifiedTotal:number;illustrativeTotal:number;remaining:number;overBudget:number;utilization:number;categories:{name:string;total:number;unpricedItems:number}[];unpricedItems:string[]};
const headers=()=>({ 'Content-Type':'application/json', ...(localStorage.getItem('ps_token') ? {Authorization:`Bearer ${localStorage.getItem('ps_token')}`} : {}) });
export async function request<T>(path:string, options:RequestInit={}) : Promise<T>{
 const response=await fetch(`${API}${path}`,{...options,headers:{...headers(),...options.headers}}); const body= response.status===204 ? null : await response.json().catch(()=>({}));
 if(!response.ok) throw new Error(body.detail || 'The request could not be completed.'); return body as T;
}
export const formatMoney=(minor:number)=>new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0}).format(minor/100);
