/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CeleryMetrics } from './CeleryMetrics';
import type { MinioMetrics } from './MinioMetrics';
import type { PostgresMetrics } from './PostgresMetrics';
import type { RedisMetrics } from './RedisMetrics';
export type SystemHealthResponse = {
    fastapi_latency_ms: number;
    postgres: PostgresMetrics;
    redis: RedisMetrics;
    celery: CeleryMetrics;
    minio: MinioMetrics;
};

