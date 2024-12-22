# OSGeo GDAL
FROM osgeo/gdal:ubuntu-small-3.6.3

# 切換工作目錄
WORKDIR /usr/src/app

# 安裝 Python與PostgreSQL bin
RUN apt-get update && apt-get install -y \
    python3-pip python3-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安裝 GDAL Python 套件
RUN pip3 install --upgrade pip \
    && pip3 install gdal \
    && pip3 install psycopg2-binary \
    && pip3 install numpy \
    && pip3 install python-dotenv

# 複製程式碼
COPY . .

# 設定容器啟動後的預設指令
# CMD ["bash"]
CMD ["python", "__main__.py"]