<template>
  <div class="script-runner">
    <h2>脚本执行器</h2>

    <!-- 脚本选择 -->
    <div>
      <label>选择脚本:</label>
      <select v-model="selectedScript">
        <option v-for="s in scripts" :key="s.script" :value="s.script">{{ s.script }}</option>
      </select>
    </div>

    <!-- 配置文件选择 -->
    <div>
      <label>选择配置:</label>
      <select v-model="selectedConfig">
        <option v-for="cfg in configs" :key="cfg.name" :value="cfg.name">{{ cfg.name }}</option>
      </select>
    </div>

    <!-- 动态参数表单 -->
    <div v-if="params.length">
      <h3>参数设置</h3>
      <div v-for="param in params" :key="param.name" class="param-item">
        <label>{{ param.name }} ({{ param.help }}):</label>
        <input
          v-if="param.type === 'int' || param.type === 'float'"
          type="number"
          v-model.number="param.value"
          :step="param.type === 'float' ? 0.1 : 1"
        />
        <input
          v-else
          type="text"
          v-model="param.value"
        />
      </div>
    </div>

    <button @click="runScript" :disabled="!selectedScript || !selectedConfig">运行</button>

    <!-- 日志显示 -->
    <div class="logs" v-if="logLines.length">
      <h3>实时日志</h3>
      <pre v-for="line in logLines" :key="line">{{ line }}</pre>
    </div>
  </div>
</template>

<script lang="ts">
import { ref, watch } from 'vue';
import axios from 'axios';

export default {
  name: "ScriptRunner",
  setup() {
    const scripts = ref<Array<any>>([]);
    const configs = ref<Array<any>>([]);
    const selectedScript = ref("");
    const selectedConfig = ref("");
    const params = ref<Array<any>>([]);
    const logLines = ref<string[]>([]);
    let ws: WebSocket | null = null;

    // 获取脚本列表
    const fetchScripts = async () => {
      try {
        const res = await axios.get("/api/v1/scripts/list");
        scripts.value = res.data;
        if (scripts.value.length) {
          selectedScript.value = scripts.value[0].script;
          updateConfigs();
        }
      } catch (err) {
        console.error("获取脚本列表失败", err);
      }
    };

    // 更新配置文件列表
    const updateConfigs = () => {
      const s = scripts.value.find((x: any) => x.script === selectedScript.value);
      configs.value = s ? s.configs : [];
      if (configs.value.length) selectedConfig.value = configs.value[0].name;
    };

    // 根据配置文件获取参数
    const fetchParams = async () => {
      if (!selectedScript.value || !selectedConfig.value) return;
      try {
        const res = await axios.get(`/api/v1/scripts/config/${selectedScript.value}/${selectedConfig.value}`);
        // 初始化 value 为默认值
        params.value = res.data.map((p: any) => ({ ...p, value: p.default }));
      } catch (err) {
        console.error("获取参数失败", err);
      }
    };

    watch(selectedScript, () => {
      updateConfigs();
      params.value = [];
    });

    watch(selectedConfig, () => {
      fetchParams();
    });

    // 运行脚本
    const runScript = async () => {
  if (!selectedScript.value || !selectedConfig.value) return;
  logLines.value = [];

  const args = params.value.map(p => `--${p.name}=${p.value}`);

  try {
    const res = await axios.post("/api/v1/scripts/run", {
      script: selectedScript.value,
      config_name: selectedConfig.value,
      args: args
    });

    if (!res.data.execution_id) {
      console.error("后端没有返回 execution_id", res.data);
      return;
    }

    const execution_id = res.data.execution_id;

    // 先关闭旧 ws
    if (ws) ws.close();

    // 创建新的 WebSocket
    ws = new WebSocket(`ws://${window.location.hostname}:8000/api/v1/scripts/ws/${execution_id}`);
    ws.onopen = () => console.log("WebSocket connected");
    ws.onmessage = (event) => {
      logLines.value.push(event.data);
    };
    ws.onclose = () => console.log("WebSocket closed");

  } catch (err) {
    console.error("运行脚本失败", err);
  }
};


    fetchScripts();

    return {
      scripts,
      configs,
      selectedScript,
      selectedConfig,
      params,
      logLines,
      runScript
    };
  }
};
</script>

<style scoped>
.logs {
  margin-top: 20px;
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 10px;
  height: 300px;
  overflow-y: scroll;
  font-family: monospace;
}
.param-item {
  margin-bottom: 10px;
}
</style>
