package org.ananas.mcpserver.model;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
public class CurrentCondition {
    private String feelsLikeC;
    private String humidity;
    private String localObsDateTime;
    private String precipMM;
    private String pressure;
    private String temp_C;
    private String uvIndex;
    private String visibility;
    private List<WeatherDesc> weatherDesc;
    private String winddir16Point;
    private String windspeedKmph;
}
