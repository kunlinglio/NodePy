/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type FinancialSymbolStats = {
    symbol: string;
    type: FinancialSymbolStats.type;
    is_history_complete: boolean;
    record_count: number;
    oldest_data: (number | null);
    latest_data: (number | null);
    data_gap_ratio: number;
    is_active: boolean;
};
export namespace FinancialSymbolStats {
    export enum type {
        CRYPTO = 'crypto',
        STOCK = 'stock',
    }
}

