package org.ananas.mcpserver.service;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.client.RestClient;
import org.ananas.mcpserver.model.WeatherResponse;
import org.ananas.mcpserver.model.CurrentCondition;

@Service
public class WeatherServiceImpl implements WeatherService {

    private static final String BASE_URL = "https://wttr.in";

    private final RestClient restClient;

    public WeatherServiceImpl() {
        this.restClient = RestClient.builder()
                .baseUrl(BASE_URL)
                .defaultHeader("Accept", "application/geo+json")
                .defaultHeader("User-Agent", "WeatherApiClient/1.0 (your@email.com)")
                .build();
    }

    @Override
    @Tool(description = "获取中国城市的当前天气信息。输入为城市名称（例如：杭州、上海）")
    public String getWeather(@RequestParam("arg0")String cityName) {
        System.out.println("调用天气mcp服务WeatherServiceImpl!");
        WeatherResponse response = restClient.get()
                .uri("/{city_name}?format=j1", cityName)
                .retrieve()
                .body(WeatherResponse.class);
        if (response != null && response.getCurrent_condition() != null && !response.getCurrent_condition().isEmpty()) {
            CurrentCondition currentCondition = response.getCurrent_condition().get(0);
            String result = String.format("""
                            城市: %s
                            天气情况: %s
                            气压: %s（mb）
                            温度: %s°C (Feels like: %s°C)
                            湿度: %s%%
                            降水量:%s (mm)
                            风速: %s km/h (%s)
                            能见度: %s 公里
                            紫外线指数: %s
                            观测时间: %s
                            """,
                    cityName,
                    currentCondition.getWeatherDesc().get(0).getValue(),
                    currentCondition.getPressure(),
                    currentCondition.getTemp_C(),
                    currentCondition.getFeelsLikeC(),
                    currentCondition.getHumidity(),
                    currentCondition.getPrecipMM(),
                    currentCondition.getWindspeedKmph(),
                    currentCondition.getWinddir16Point(),
                    currentCondition.getVisibility(),
                    currentCondition.getUvIndex(),
                    currentCondition.getLocalObsDateTime()
            );
            return result;
        } else {
            return "无法获取天气信息，请检查城市名称是否正确或稍后重试。";
        }
    }
}
