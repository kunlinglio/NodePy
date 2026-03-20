<template>
    <div class="DatetimeComputeNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='datetimeProcess'>日期偏移</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-datetime port">
                <div class="input-port-description">
                    日期
                </div>
                <Handle id="datetime" type="target" :position="Position.Left" :class="[`${datetime_type}-handle-color`, {'node-errhandle': datetimeHasErr.value}]"/>
            </div>
            <div class="input-value port">
                <div class="input-port-description" :class="{'node-has-paramerr': valueHasErr.value}">
                    数值
                </div>
                <Handle id="value" type="target" :position="Position.Left" :class="[`${value_type}-handle-color`, {'node-errhandle': inputValueHasErr.value}]"/>
            </div>
            <div class="value">
                <NodepyNumberInput
                    v-if="data.param.data_type === 'int'"
                    v-model="value"
                    class="nodrag"
                    @update-value="() => {
                        updateSimpleStringNumberBoolValue(data.param, 'value', value)
                    }"
                    :disabled="valueDisabled"
                    :allow-empty="true"
                />
                <NodepyNumberInput
                    v-else-if="data.param.data_type === 'float'"
                    v-model="value"
                    class="nodrag"
                    @update-value="() => {
                        updateSimpleStringNumberBoolValue(data.param, 'value', value)
                    }"
                    :denominator="1000"
                    :disabled="valueDisabled"
                    :allow-empty="true"
                 />
            </div>
            <div class="data_type">
                <div class="param-description" :class="{'node-has-paramerr': data_typeHasErr.value}">
                    数据类型
                </div>
                <NodepySelectFew
                    :options="data_typeUi"
                    :default-selected="defaultSelectedData_type"
                    @select-change="(e) => {
                        updateSimpleSelectFew(data.param, 'data_type', data_type, e)
                        if(data.param.data_type === 'int') {
                            value = Math.floor(value || 0)
                            updateSimpleStringNumberBoolValue(data.param, 'value', value)
                        }
                    }"
                    :disabled="valueDisabled"
                    class="nodrag"
                />
            </div>
            <div class="op">
                <div class="param-description" :class="{'node-has-paramerr': opHasErr.value}">
                    运算
                </div>
                <NodepySelectFew
                    :options="opChinese"
                    :default-selected="defaultSelectedOp"
                    @select-change="(e) => updateSimpleSelectFew(data.param, 'op', op, e)"
                    class="nodrag"
                />
            </div>
            <div class="unit">
                <div class="param-description" :class="{'node-has-paramerr': unitHasErr.value}">
                    数值单位
                </div>
                <NodepySelectMany
                    :options="unitChinese"
                    :default-selected="defaultSelectedUnit"
                    @select-change="(e) => updateSimpleSelectMany(data.param, 'unit', unit, e)"
                    class="nodrag"
                />
            </div>
            <div class="output-result port">
                <div class="output-port-description">
                    结果输出
                </div>
                <Handle id="result" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': resultHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed, watch} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import { getInputType } from '../getInputType'
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepySelectFew from '../tools/Nodepy-selectFew.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import { hasInputEdge } from '../hasEdge'
    import { updateSimpleStringNumberBoolValue, updateSimpleSelectFew, updateSimpleSelectMany } from '../updateParam'
    import type { DatetimeComputeNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<DatetimeComputeNodeData>>()
    const value = ref(props.data.param.value)
    const valueDisabled = computed(() => hasInputEdge(props.id, 'value'))
    const data_type = ['int', 'float']
    const data_typeUi = ['整数', '浮点数']
    const defaultSelectedData_type = [data_type.indexOf(props.data.param.data_type)]
    const op = ["ADD", "SUB"]
    const opChinese = ['加法', '减法']
    const defaultSelectedOp = [op.indexOf(props.data.param.op)]
    const unit = ["DAYS", "HOURS", "MINUTES", "SECONDS"]
    const unitChinese = ['天', '小时', '分钟', '秒']
    const defaultSelectedUnit = unit.indexOf(props.data.param.unit)
    const datetime_type = computed(() => getInputType(props.id, 'datetime'))
    const value_type = computed(() => getInputType(props.id, 'value'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['result']?.type || 'default')
    const resultHasErr = computed(() => handleOutputError(props.id, 'result'))
    const errMsg = ref<string[]>([])
    const valueHasErr = ref({
        id: 'value',
        value: false
    })
    const data_typeHasErr = ref({
        id: 'data_type',
        value: false
    })
    const opHasErr = ref({
        id: 'op',
        value: false
    })
    const unitHasErr = ref({
        id: 'unit',
        value: false
    })
    const datetimeHasErr = ref({
        handleId: 'datetime',
        value: false
    })
    const inputValueHasErr = ref({
        handleId: 'value',
        value: false
    })


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, valueHasErr, data_typeHasErr, opHasErr, unitHasErr)
        handleValidationError(props.id, props.data.error, errMsg, datetimeHasErr, inputValueHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .DatetimeComputeNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-datetime {
                margin-bottom: $node-margin;
            }
            .input-value {
                margin-bottom: 2px;
            }
            .value, .data_type, .op, .unit {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color[data-handleid="datetime"] {
        background: $datetime-color;
    }
    .all-handle-color[data-handleid="value"] {
        background: linear-gradient(to bottom, $int-color 0 50%, $float-color 50% 100%);
    }
</style>
