<template>
    <div class="MapColumnEndNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="control">列映射结束</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-remains port">
                <div class="input-port-description">
                    剩余列
                </div>
                <Handle id="remains" type="target" :position="Position.Left" :class="[`${remains_type}-handle-color`, {'node-errhandle': inputRemainsHasErr.value}]"/>
            </div>
            <div class="input-cell port">
                <div class="input-port-description">
                    单元格
                </div>
                <Handle id="cell" type="target" :position="Position.Left" :class="[`${cell_type}-handle-color`, {'node-errhandle': inputCellHasErr.value}]"/>
            </div>
            <div class="result_col">
                <div class="param-description" :class="{'node-has-paramerr': result_colHasErr.value}">
                    结果列
                </div>
                <NodepyStringInput 
                    v-model="result_col" 
                    @update-value="() => updateSimpleStringNumberBoolValue(data.param, 'result_col', result_col)" 
                    class="nodrag" 
                    placeholder="结果列名"
                />
            </div>
            <div class="output-table port">
                <div class="output-port-description">
                    输出
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
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import { updateSimpleStringNumberBoolValue } from '../updateParam'
    import type { MapColumnEndNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<MapColumnEndNodeData>>()
    const result_col = ref(props.data.param.result_col)
    const remains_type = computed(() => getInputType(props.id, 'remains'))
    const cell_type = computed(() => getInputType(props.id, 'cell'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const outputTableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const errMsg = ref<string[]>([])
    const result_colHasErr = ref({
        id: 'result_col',
        value: false
    })
    const inputRemainsHasErr = ref({
        handleId: 'remains',
        value: false
    })
    const inputCellHasErr = ref({
        handleId: 'cell',
        value: false
    })


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, result_colHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputRemainsHasErr, inputCellHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .MapColumnEndNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-remains, .input-cell {
                margin-bottom: $node-margin;
            }
            .result_col {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color[data-handleid="remains"] {
        background: $table-color;
    }
    .all-handle-color[data-handleid="cell"] {
        background: $default-type-color;
    }
</style>