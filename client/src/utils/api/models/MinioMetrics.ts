/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type MinioMetrics = {
    status: MinioMetrics.status;
    latency_ms?: (number | null);
    bucket_count: number;
    buckets: Array<string>;
    error?: (string | null);
};
export namespace MinioMetrics {
    export enum status {
        HEALTHY = 'healthy',
        UNHEALTHY = 'unhealthy',
    }
}

