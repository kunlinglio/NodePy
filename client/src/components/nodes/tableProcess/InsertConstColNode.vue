<template>
    <div class="InsertConstColNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="tableProcess">添加常量列</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="input-const_value port">
                <div class="input-port-description" :class="{'node-has-paramerr': const_valueHasErr.value}">
                    常量
                </div>
                <Handle id="const_value" type="target" :position="Position.Left" :class="[`${const_value_type}-handle-color`, {'node-errhandle': inputConst_valueHasErr.value}]"/>
            </div>
            <div class="const_value">
                <NodepyNumberInput
                    v-if="data.param.col_type === 'int'"
                    v-model="const_value_number"
                    class="nodrag"
                    @update-value="() => {
                        updateSimpleStringNumberBoolValue(data.param, 'const_value', const_value_number)
                        updateSimpleStringNumberBoolValue(data.param, 'const_value_number', const_value_number)
                    }"
                    :disabled="const_valueDisabled"
                    :allow-empty="true"
                />
                <NodepyNumberInput
                    v-else-if="data.param.col_type === 'float'"
                    v-model="const_value_number"
                    class="nodrag"
                    @update-value="() => {
                        updateSimpleStringNumberBoolValue(data.param, 'const_value', const_value_number)
                        updateSimpleStringNumberBoolValue(data.param, 'const_value_number', const_value_number)
                    }"
                    :denominator="1000"
                    :disabled="const_valueDisabled"
                    :allow-empty="true"
                 />
                <NodepyStringInput 
                    v-else-if="data.param.col_type === 'str'"
                    v-model="const_value_str" 
                    @update-value="() => {
                        updateSimpleStringNumberBoolValue(data.param, 'const_value', const_value_str)
                        updateSimpleStringNumberBoolValue(data.param, 'const_value_str', const_value_str)
                    }" 
                    class="nodrag" 
                    placeholder="常量字符串"
                    :disabled="const_valueDisabled"
                />
                <NodepyBoolValue
                    v-else-if="data.param.col_type === 'bool'"
                    v-model="const_value_bool"
                    @update-value="() => {
                        updateSimpleStringNumberBoolValue(data.param, 'const_value', const_value_bool)
                        updateSimpleStringNumberBoolValue(data.param, 'const_value_bool', const_value_bool)
                    }"
                    width="20px"
                    height="20px"
                    :disabled="const_valueDisabled"
                >
                    布尔值
                </NodepyBoolValue>
                <NodepyStringInput
                    v-else-if="data.param.col_type === 'Datetime'"
                    v-model="const_value_datetime"
                    @update-value="() => {
                        updateSimpleStringNumberBoolValue(data.param, 'const_value', const_value_datetime)
                        updateSimpleStringNumberBoolValue(data.param, 'const_value_datetime', const_value_datetime)
                    }"
                    class="nodrag"
                    placeholder="日期时间"
                    :disabled="const_valueDisabled"
                />
            </div>
            <div class="col_name">
                <div class="param-description" :class="{'node-has-paramerr': col_nameHasErr.value}">
                    新增列
                </div>
                <NodepyStringInput v-model="col_name" @update-value="() => updateSimpleStringNumberBoolValue(data.param, 'col_name', col_name)" class="nodrag" placeholder="新增的列名"/>
            </div>
            <div class="col_type">
                <div class="param-description" :class="{'node-has-paramerr': col_typeHasErr.value}">
                    数据类型
                </div>
                <NodepySelectMany
                    :options="col_typeUi"
                    :default-selected="defaultSelectedCol_type"
                    @select-change="(e) => {
                        updateSimpleSelectMany(data.param, 'col_type', col_type, e)
                        if(data.param.col_type === 'int') {
                            const_value_number = Math.floor(const_value_number || 0)
                            updateSimpleStringNumberBoolValue(data.param, 'const_value_number', const_value_number)
                            updateSimpleStringNumberBoolValue(data.param, 'const_value', const_value_number)
                        }
                    }"
                    class="nodrag"
                />
            </div>
            <div class="output-table port">
                <div class="output-port-description">
                    表格输出
                </div>
                <Handle id="table" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': outputTableHasErr}]"/>
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
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import NodepyBoolValue from '../tools/Nodepy-boolValue.vue'
    import { updateSimpleStringNumberBoolValue, updateSimpleSelectMany } from '../updateParam'
    import { hasInputEdge } from '../hasEdge'
    import type { InsertConstColNodeData } from '@/types/nodeTypes'
    import { dataTypeColor } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<InsertConstColNodeData>>()
    const const_value_number = ref(props.data.param.const_value_number)
    const const_value_str = ref(props.data.param.const_value_str)
    const const_value_bool = ref(props.data.param.const_value_bool)
    const const_value_datetime = ref(props.data.param.const_value_datetime)
    const const_valueDisabled = computed(() => hasInputEdge(props.id, 'const_value'))
    const col_type = ["int", "float", "bool", "str", "Datetime"]
    const col_typeUi = ['整数', '浮点数', '布尔值', '字符串', '时间']
    const defaultSelectedCol_type = col_type.indexOf(props.data.param.col_type)
    const col_name = ref(props.data.param.col_name)
    const table_type = computed(() => getInputType(props.id, 'table'))
    const const_value_type = computed(() => getInputType(props.id, 'const_value'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const outputTableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const errMsg = ref<string[]>([])
    const col_nameHasErr = ref({
        id: 'col_name',
        value: false
    })
    const col_typeHasErr = ref({
        id: 'col_type',
        value: false
    })
    const const_valueHasErr = ref({
        id: 'const_value',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })
    const inputConst_valueHasErr = ref({
        handleId: 'const_value',
        value: false
    })
    const const_valueHandleColor = computed(() => {
        switch(props.data.param.col_type) {
            case 'int':
                return dataTypeColor.int
            case 'float':
                return dataTypeColor.float
            case 'bool':
                return dataTypeColor.bool
            case 'str':
                return dataTypeColor.str
            case 'Datetime':
                return dataTypeColor.Datetime
        }
    })


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, col_nameHasErr, col_typeHasErr, const_valueHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr, inputConst_valueHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .InsertConstColNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .input-const_value {
                margin-bottom: 2px;
            }
            .col_name, .col_type, .const_value {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color[data-handleid="table"] {
        background: $table-color;
    }
    .all-handle-color[data-handleid="const_value"] {
        background: v-bind(const_valueHandleColor);
    }
</style>
