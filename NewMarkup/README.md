Syntax Example for a font with a flexible shadow axis (@RobertPraley)
```json
"Master Relations": {
		"Regular": {
			"Bold":{},
			"Light":{},
			"Shadow": {
				"ShadowAngle": {}
			}
		}
	},
	"Master Mapping": {
		"Regular":				[0,1],
			"Bold":				[85,160],
			"Light":			[85,20],
			"Shadow":			[0,1],
				"ShadowAngle":	[45,-45]
	},
	"Axes": {
		"WeightAxes": [["Light", "Regular", "Bold"]]
	},

	"InstancesSetup": {
		"VariableFont":	{
			"Slider": {
				"[wght]Weight.slider":			[[1, 220], "WeightAxes"],
				"[SHDW]Shadow.slider":			[0, 1],
				"[SHDA]ShadowAngle.slider":		[-45, 45]
			},
			"Master": {
				"Shadow": 		"$SliderShadow * map($[wght]Weight.slider,20,220,0,1)"
			}
		}
	}
```
