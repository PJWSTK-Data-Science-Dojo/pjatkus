module.exports = {
  apps: [
    {
      name: 'pjatkus-llm',
      script: './.venv/bin/uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8002',
      cwd: './services/llm',
      interpreter: 'none',
      env_file: '../../.env',
      env: {
        PYTHONPATH: '../..:$PYTHONPATH',
        OPENAI_API_KEY: process.env.OPENAI_API_KEY,
        OPENAI_MODEL: 'gpt-4o-mini'
      },
      error_file: './logs/llm-error.log',
      out_file: './logs/llm-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'pjatkus-stt',
      script: './.venv/bin/uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8001',
      cwd: './services/stt',
      interpreter: 'none',
      env_file: '../../.env',
      env: {
        PYTHONPATH: '../..:$PYTHONPATH',
        NEMO_MODEL: 'nvidia/stt_pl_fastconformer_hybrid_large_pc',
        CUDA_VISIBLE_DEVICES: '0'
      },
      error_file: './logs/stt-error.log',
      out_file: './logs/stt-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'pjatkus-gateway',
      script: './.venv/bin/uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000',
      cwd: './services/gateway',
      interpreter: 'none',
      env_file: '../../.env',
      env: {
        PYTHONPATH: '../..:$PYTHONPATH',
        STT_SERVICE_URL: 'http://localhost:8001',
        LLM_SERVICE_URL: 'http://localhost:8002',
        REQUEST_TIMEOUT: '30'
      },
      error_file: './logs/gateway-error.log',
      out_file: './logs/gateway-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};