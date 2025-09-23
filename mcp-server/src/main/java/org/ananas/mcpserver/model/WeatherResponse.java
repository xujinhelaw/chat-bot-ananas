package org.ananas.mcpserver.model;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
public class WeatherResponse {
    private List<CurrentCondition> current_condition;
}
