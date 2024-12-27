# import requests module 
import logging
import json
import requests
import hashlib
import os

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s',
                    filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

aqi_url = "https://api.breezometer.com/air-quality/v2/current-conditions?lang=en&key=496bfcfb6ddd40ef831e29858c8ba7a9&metadata=extended_aqi&features=breezometer_aqi,local_aqi,health_recommendations,sources_and_effects,dominant_pollutant_concentrations,pollutants_concentrations,all_pollutants_concentrations,pollutants_aqi_information&lat=28.5561437&lon=77.0999623&all_aqi=true"
 
json_file_path = "./"
json_file_name = "aqi_v2.json"

def get_truncate_file(file_path):
    file_path.seek(0)
    file_path.truncate()

def get_aqi_index(api_url,json_file_path):
    try:
        logging.info("Calling aqi get_aqi_index")
        response = requests.request("GET", api_url, headers={'Content-Type': 'application/json'},timeout=20)
        if response.status_code == 200: #can improve the code with response.raise_for_status() 
            response_data = json.loads(response.text)
            # print(response_data)
            if response_data.get('data', {}) and response_data.get('data').get('indexes', False):
                if response_data.get('data').get('indexes').get('ind_cpcb'):
                    response_formatted_data =  response_data.get('data').get('indexes').get('ind_cpcb')
                    file_path = os.path.join(json_file_path, json_file_name)
                    if os.path.isfile(file_path):
                        with open(file_path, 'r+') as aqi_exist_file:
                            json_file = json.load(aqi_exist_file)
                            file_checksum = hashlib.sha256(str(json_file).encode()).hexdigest()
                            response_checksum = hashlib.sha256(str(response_formatted_data).strip().encode()).hexdigest()
                            # logging.info("Checksum value is of score: %s" % (file_checksum != response_checksum))
                            file_checksum == response_checksum and logging.info("Checksum is %s \t No update in File- %s" %(file_checksum != response_checksum,json_file_path))
                            if file_checksum != response_checksum:
                                logging.info("Checksum is %s \t File-%s is updating " %(file_checksum != response_checksum,json_file_path))
                                get_truncate_file(aqi_exist_file)
                                json.dump(response_formatted_data, aqi_exist_file)
                            aqi_exist_file.close()
                    else:
                        with open(file_path, 'w+') as score_json_file:
                            json.dump(response_formatted_data, score_json_file)
                            score_json_file.close()
                else:
                    logging.debug("No key found for response_data.get('data').get('indexes').get('ind_cpcb') %s\n\n",response_data.get('data').get('indexes'))
            else:
                logging.debug("No data found!!! %s\n\n",response_data)
        else:
            logging.error("Api is not working properly!,response code: %s", response.status_code)
    except Timeout:
        logging.error("Request timed out.")
    except RequestException as e:
        logging.error(f"Request failed: {e}")
    except json.JSONDecodeError:
        logging.error("Failed to parse JSON response.")
    except Exception as e:
        logging.error("Unexpected error occurred", exc_info=True)

def main():
    if not os.path.exists(json_file_path):
        os.makedirs(json_file_path)
    get_aqi_index(aqi_url,json_file_path)

if __name__ == '__main__':
    main()
