#!/bin/bash

# 设置变量
DATA_PATH="data/test.csv"
CONFIG_PATH="config/PromptHub.yaml"
SAVE_PATH="data/test_data/disaster_prediction.json"
PORT="8000"

# 创建日志目录
LOG_DIR="logs"
mkdir -p $LOG_DIR

# 生成时间戳
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 设置日志文件路径
LOG_FILE="${LOG_DIR}/test/disaster_prediction_${TIMESTAMP}.log"

# 打印运行信息
echo "Running disaster prediction script..."
echo "Data path: $DATA_PATH"
echo "Config path: $CONFIG_PATH"
echo "Save path: $SAVE_PATH"
echo "Port: $PORT"
echo "Log file: $LOG_FILE"

# 运行 Python 脚本并保存日志
python main.py --state "infer_llamafactory" --data_path $DATA_PATH --config_path $CONFIG_PATH --save_path $SAVE_PATH --port $PORT

# 检查运行是否成功
if [ $? -eq 0 ]; then
    echo "Script completed successfully. Logs can be found at $LOG_FILE"
else
    echo "Script encountered errors. Check the logs at $LOG_FILE for details."
fi