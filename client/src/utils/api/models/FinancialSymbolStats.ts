/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type FinancialSymbolStats = {
    symbol: string;
    type: FinancialSymbolStats.type;
    completed: boolean;
    oldest_data: string;
};
export namespace FinancialSymbolStats {
    export enum type {
        CRYPTO = 'crypto',
        STOCK = 'stock',
    }
}

