import httpx
from dotenv import load_dotenv
from os import getenv
from sys import exit
from mcp.server import FastMCP
# encoding: utf-8
load_dotenv()

APP_NAME = getenv('APP_NAME', 'JackTools')
APP_PORT = int(getenv('APP_PORT', 3001))
AMAP_KEY = getenv('AMAP_KEY', '')

if AMAP_KEY == '':
    print("请在 .env 文件中设置 AMAP_KEY")
    exit(1)

# # 初始化 FastMCP 服务器
app = FastMCP(APP_NAME, port=APP_PORT)


@app.tool()
async def query_adcode(query: str) -> str:
    """
    高德城市编码搜索

    Args:
        query: 城市名称

    Returns:
        adcode: 城市编码
    """
    global AMAP_KEY
    async with httpx.AsyncClient() as client:
        headers = {
            #'Authorization': '换成你自己的API KEY',
            #'Content-Type': 'application/json',
        }
        json_data = {}
        params = {
            'key': AMAP_KEY,
            'keywords': query,
            'subdistrict': 0,
            'extensions': 'base',
        }

        response = await client.get(
            'https://restapi.amap.com/v3/config/district',
            #headers = headers,
            #json = json_data,
            params = params,
        )

        res_data = response.json()
        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"
        if res_data['status'] != '1':
            return f"Error: {res_data['info']}"
        
        # res_data = []
        # for choice in response.json()['choices']:
        #     for message in choice['message']['tool_calls']:
        #         search_results = message.get('search_result')
        #         if not search_results:
        #             continue
        #         for result in search_results:
        #             res_data.append(result['content'])

        # return '\n\n\n'.join(res_data['districts'][0]['adcode'])
        if 'districts' in res_data and len(res_data['districts']) > 0:
            return res_data['districts'][0]['adcode']
        return f"Error: No adcode found for query '{query}'"

@app.tool()
async def query_live_weather(query: str) -> str:
    """
    高德天气搜索实况天气数据信息, 注意: 需要先获取城市编码(query_adcode)

    Args:
        query: adcode: 城市编码

    Returns:
        搜索结果的总结
    """
    adcode: str
    async with httpx.AsyncClient() as client:
        # params = {
        #     'key': AMAP_KEY,
        #     'keywords': query,
        #     'subdistrict': 0,
        #     'extensions': 'base',
        # }
        # 
        # response = await client.get(
        #     'https://restapi.amap.com/v3/config/district',
        #     params = params,
        # )
        # 
        # res_data = response.json()
        # if response.status_code != 200:
        #     return f"Error: Failed to get adcode {response.status_code} - {response.text}"
        # if res_data['status'] != '1':
        #     return f"Error: Failed to get adcode Error: {res_data['info']}"
        # if 'districts' in res_data and len(res_data['districts']) > 0:
        #     adcode = res_data['districts'][0]['adcode']
        # else:
        #     return f"Error: Failed to get adcode, No adcode found for query '{query}'"
        #adcode = await query_adcode(query)
        adcode = query

    # async with httpx.AsyncClient() as client:
        headers = {
            #'Authorization': '换成你自己的API KEY',
            #'Content-Type': 'application/json',
        }
        json_data = {}
        params = {
            'key': AMAP_KEY,
            'city': adcode,
            'extensions': 'base',
        }

        response = await client.get(
            'https://restapi.amap.com/v3/weather/weatherInfo',
            #headers = headers,
            #json = json_data,
            params = params,
        )

        
        if response.status_code != 200:
            return f"Error: Failed to get weatherInfo, Error: {response.status_code} - {response.text}"
        res_data = response.json()
        if res_data['status'] != '1':
            return f"Error: Failed to get weatherInfo, Error: {res_data['info']}"
        # res_data = []
        # for choice in response.json()['choices']:
        #     for message in choice['message']['tool_calls']:
        #         search_results = message.get('search_result')
        #         if not search_results:
        #             continue
        #         for result in search_results:
        #             res_data.append(result['content'])
        rt_msg = '实况天气数据信息\n'
        for live in res_data['lives']:
            rt_msg += '\n'
            rt_msg += f"城市: {live['city']}\n"
            rt_msg += f"天气: {live['weather']}\n"
            rt_msg += f"温度: {live['temperature']}°C\n"
            rt_msg += f"湿度: {live['humidity']}%\n"
            rt_msg += f"风速: {live['windpower']}级\n"
            rt_msg += f"风向: {live['winddirection']}\n"
            rt_msg += f"发布时间: {live['reporttime']}\n\n\n"

        return rt_msg
        #return '\n\n\n'.join(res_data['lives'])
    

@app.tool()
async def query_forecast_weather(query: str) -> str:
    """
    高德天气搜索预报天气数据信息, 注意: 需要先获取城市编码(query_adcode)

    Args:
        query: adcode: 城市编码

    Returns:
        搜索结果的总结
    """
    adcode: str
    async with httpx.AsyncClient() as client:
        adcode = query

        # 获取预测
        params = {
            'key': AMAP_KEY,
            'city': adcode,
            'extensions': 'all',
        }

        response = await client.get(
            'https://restapi.amap.com/v3/weather/weatherInfo',
            #headers = headers,
            #json = json_data,
            params = params,
        )

        if response.status_code != 200:
            return f"Error: Failed to get weatherInfo, Error: {response.status_code} - {response.text}"
        
        res_data = response.json()
        if res_data['status'] != '1':
            return f"Error: Failed to get weatherInfo, Error: {res_data['info']}"
        
        if 'forecasts' in res_data and len(res_data['forecasts']) > 0 and 'casts' in res_data['forecasts'][0]:
            rt_msg = f'预报{res_data['forecasts'][0]['city']}天气数据信息\n'
            rt_msg += f"发布时间: {res_data['forecasts'][0]['reporttime']}\n\n"
            for forecast in res_data['forecasts'][0]['casts']:
                # rt_msg += f"城市: {forecast['city']}\n"
                rt_msg += f"日期: {forecast['date']}\n"
                rt_msg += f"星期: {forecast['week']}\n"
                rt_msg += f"白天天气: {forecast['dayweather']}\n"
                rt_msg += f"夜晚天气: {forecast['nightweather']}\n"
                rt_msg += f"白天温度: {forecast['daytemp']}°C\n"
                rt_msg += f"夜晚温度: {forecast['nighttemp']}级\n"
                rt_msg += f"白天风向: {forecast['daywind']}\n"
                rt_msg += f"晚上风向: {forecast['nightwind']}\n"
                rt_msg += f"白天风速: {forecast['daypower']}级\n"
                rt_msg += f"晚上风速: {forecast['nightpower']}级\n"
                rt_msg += "\n\n"
        return rt_msg

if __name__ == "__main__":
    app.run(transport='sse')