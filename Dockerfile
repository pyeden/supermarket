# 写在最前面：强烈建议先阅读官方教程[Dockerfile最佳实践]（https://docs.docker.com/develop/develop-images/dockerfile_best-practices/）
# 选择构建用基础镜像（选择原则：在包含所有用到的依赖前提下尽可能提及小）。如需更换，请到[dockerhub官方仓库](https://hub.docker.com/_/python?tab=tags)自行选择后替换。

# 选择基础镜像
FROM python:3.8.12-slim-buster

# 拷贝当前项目到/app目录下
COPY .pip ~/.pip
COPY . /app

# 设定当前的工作目录
WORKDIR /app

RUN /usr/local/bin/python -m pip install --upgrade pip\
    &&pip install --user -r requirements.txt

# 设定对外端口
EXPOSE 8088

# 设定启动命令
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8088"]