import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(".env")
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USEE = os.getenv("DB_USEE")
DB_PASSWORD = os.getenv("DB_PASSWORD")
SCHEMAS = os.getenv("SCHEMAS")

BASE_PATH = "/data"
SHP_DIR = BASE_PATH + "/shp"
GEOJSON_DIR = BASE_PATH + "/geojson"
OGR2OGR_EXECUTE = "/usr/bin/ogr2ogr"

class shp2pgsql:
    conn = None

    def __init__(self):
        self.__init_db_connect()
        pass

    def __init_db_connect(self):
        try:
            self.conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_DATABASE,
            user=DB_USEE,
            password=DB_PASSWORD)
        except:
            print("[ERROR] The pgsql connection fail")
            pass

    def importDataToPostgres(self, file, table_name):
        global OGR2OGR_EXECUTE, DB_HOST, DB_DATABASE, DB_USEE, DB_PASSWORD
        
        table_exist = self.checkShapeTableExist(table_name)
        if table_exist == False:
            command = OGR2OGR_EXECUTE + ' -f PostgreSQL PG:"host=' + DB_HOST + ' user=' + DB_USEE + ' password=' + DB_PASSWORD + ' dbname=' + DB_DATABASE + '" ' + file + ' -nln ' + SCHEMAS + '.' + table_name + ' -lco FID=gid -lco GEOMETRY_NAME=geom'
            os.system(command)
            print(f"[INFO] The table ({SCHEMAS}.{table_name}) is created.")
            return True
        else:
            print(f"[INFO] The table ({SCHEMAS}.{table_name}) is exist.")
            return False
        

    def checkShapeTableExist(self, table_name):
        cur = self.conn.cursor()
        sql = f"SELECT EXISTS ( SELECT FROM information_schema.tables WHERE table_schema = '{SCHEMAS}' AND table_name = '{table_name}');"
        cur.execute(sql)
        row = cur.fetchone()
        res = row[0]
        
        return res
 
    def getFilePathList(self, path):
        dir_list = os.listdir(path)
        return dir_list

    """
    " 將shape轉為geojson
    """     
    def convertShpToGeojson(self, table_name, file):
        geojson = os.path.join(GEOJSON_DIR, table_name.lower() + ".geojson")
        if os.path.isfile(geojson) == False:
            # TODO: using parameter with input & output variabe of SRID
            command = f"{OGR2OGR_EXECUTE} -f GeoJSON -t_srs EPSG:3824 -s_srs EPSG:3824 {geojson} {file}"
            # command = f"{OGR2OGR_EXECUTE} -f GeoJSON -t_srs EPSG:3826 -s_srs EPSG:3826 {geojson} {file}"
            # command = f"{OGR2OGR_EXECUTE} -f GeoJSON -t_srs EPSG:4326 -s_srs EPSG:4326 {geojson} {file}"
            os.system(command)
            print(f"[INFO] Convert success, result in {geojson}")
        else:
            print(f"[INFO] GeoJSON {geojson} is exist.")
        
        return geojson


    def main_shpToGeoJson(self):
        # Find all folder from shp directory
        folder_list = self.getFilePathList(SHP_DIR)
        for table_name in folder_list:
            print(f"[INFO] Convert shape file to geojson file: {table_name}")

            fileDir = os.path.join(SHP_DIR, table_name)
            fileExt = r".shp"
            shp_file_name = [_ for _ in os.listdir(fileDir) if _.endswith(fileExt)][0]
            shp_file = os.path.join(fileDir, shp_file_name)
            
            geojson = self.convertShpToGeojson(table_name, shp_file)

    def main_importGeoJSON2PostgreSQLDataBase(self):
        dir_list = self.getFilePathList(GEOJSON_DIR)
        for file_name in dir_list:
            table_name = file_name.lower()
            table_name = os.path.splitext(table_name)[0]
            geojson = os.path.join(GEOJSON_DIR, file_name)
            import_res = self.importDataToPostgres(geojson, table_name)


if __name__ == "__main__":
    if not os.path.exists(SHP_DIR):
        os.makedirs(SHP_DIR)
    if not os.path.exists(GEOJSON_DIR):
        os.makedirs(GEOJSON_DIR)
        
    shp2pgsql = shp2pgsql()
    shp2pgsql.main_shpToGeoJson()
    if shp2pgsql.conn is not None:
        shp2pgsql.main_importGeoJSON2PostgreSQLDataBase()
