import {describe,expect,it} from 'vitest';
import {formatMoney} from './api';
describe('money display',()=>{it('formats INR minor units',()=>expect(formatMoney(123450)).toContain('1,235'))});
