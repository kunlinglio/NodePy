/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PostgresMetrics = {
    status: PostgresMetrics.status;
    latency_ms?: (number | null);
    active_connections: number;
    idle_connections: number;
    total_connections: number;
    database_size?: (string | null);
    error?: (string | null);
};
export namespace PostgresMetrics {
    export enum status {
        HEALTHY = 'healthy',
        UNHEALTHY = 'unhealthy',
    }
}

