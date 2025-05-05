def get_recommendations(aqi_value, detailed=False):
    """
    Get health recommendations based on AQI value
    
    Args:
        aqi_value (float): Current AQI value
        detailed (bool): Whether to return detailed recommendations
        
    Returns:
        dict: Dictionary of recommendations
    """
    if not detailed:
        # Basic recommendations
        if aqi_value <= 50:
            return {
                'general': "Air quality is good. Enjoy your outdoor activities.",
                'outdoor': "It's a great day for outdoor exercise and activities.",
                'protection': "No special protection needed for the general population.",
                'health': "Good air quality contributes to overall health and well-being."
            }
        elif aqi_value <= 100:
            return {
                'general': "Air quality is acceptable for most individuals.",
                'outdoor': "Unusually sensitive people should consider reducing prolonged outdoor exertion.",
                'protection': "No special protection needed for most people.",
                'health': "Good time to be outdoors, but monitor your body's response if you have respiratory issues."
            }
        elif aqi_value <= 150:
            return {
                'general': "Members of sensitive groups may experience health effects.",
                'outdoor': "People with heart or lung disease, older adults, and children should limit prolonged outdoor exertion.",
                'protection': "Consider wearing masks outdoors if you belong to a sensitive group.",
                'health': "Stay hydrated and take more breaks during outdoor activities."
            }
        elif aqi_value <= 200:
            return {
                'general': "Everyone may begin to experience health effects.",
                'outdoor': "Everyone should limit prolonged outdoor exertion.",
                'protection': "Wear N95 masks outdoors. Keep windows closed at home and in vehicles.",
                'health': "Consider using air purifiers indoors. Stay well-hydrated."
            }
        elif aqi_value <= 300:
            return {
                'general': "Health alert: everyone may experience more serious health effects.",
                'outdoor': "Avoid all outdoor physical activities. Stay indoors if possible.",
                'protection': "Wear N95 masks whenever outdoors. Use air purifiers indoors.",
                'health': "Check on elderly neighbors and those with respiratory or heart conditions."
            }
        else:
            return {
                'general': "Health warning: emergency conditions. Entire population is more likely to be affected.",
                'outdoor': "Avoid all outdoor activities. Stay indoors with windows closed.",
                'protection': "Wear N95 masks even for brief outdoor exposure. Seal windows and doors if possible.",
                'health': "Use air purifiers, stay hydrated, and monitor for symptoms like coughing or shortness of breath."
            }
    else:
        # Detailed recommendations
        if aqi_value <= 50:
            return {
                'general_detailed': "Air quality is considered satisfactory, and air pollution poses little or no risk. It's a great day for outdoor activities and exercise.",
                'general_population': "No special precautions needed. Enjoy your regular outdoor activities.",
                'sensitive_groups': "For people with unusual sensitivity to air pollution, consider monitoring how you feel during outdoor activities.",
                'children': "Great air quality for children to play outdoors. Perfect time for outdoor school activities.",
                'elderly': "Excellent conditions for outdoor walks and activities.",
                'outdoor_workers': "Favorable working conditions with minimal air quality concerns.",
                'indoor_protection': [
                    "No special indoor protection needed",
                    "Good time to open windows and let fresh air in",
                    "Regular housekeeping is sufficient"
                ],
                'outdoor_protection': [
                    "No special protection required",
                    "Regular sun protection still advised",
                    "Stay hydrated during outdoor activities"
                ],
                'health_impacts': "Good air quality contributes to overall health and wellbeing. Regular exposure to clean air supports respiratory function and cardiovascular health."
            }
        elif aqi_value <= 100:
            return {
                'general_detailed': "Air quality is acceptable; however, there may be a moderate health concern for a very small number of people who are unusually sensitive to air pollution.",
                'general_population': "Most people can continue normal outdoor activities. Pay attention to your body's signals if you start feeling unwell.",
                'sensitive_groups': "People with respiratory diseases such as asthma should monitor their condition and limit prolonged outdoor exertion if symptoms occur.",
                'children': "Good conditions for outdoor play. Children with asthma should take usual precautions.",
                'elderly': "Generally good conditions for outdoor activities. Those with respiratory conditions should monitor how they feel.",
                'outdoor_workers': "Regular work activities can continue. Those with respiratory conditions should take breaks if needed.",
                'indoor_protection': [
                    "Regular ventilation is fine",
                    "Consider using air purifiers if you have respiratory issues",
                    "Standard cleaning practices are adequate"
                ],
                'outdoor_protection': [
                    "No special protection needed for most people",
                    "Sensitive individuals may want to carry relief medication",
                    "Regular sun protection and hydration advised"
                ],
                'health_impacts': "Moderate air quality generally has minimal impact on the general population, but may affect very sensitive individuals. Research shows that occasional exposure to these levels is unlikely to cause long-term effects."
            }
        elif aqi_value <= 150:
            return {
                'general_detailed': "Air quality is unhealthy for sensitive groups. Members of sensitive groups may experience health effects, but the general public is less likely to be affected.",
                'general_population': "Consider reducing prolonged or heavy outdoor exertion. Take more breaks during outdoor activities.",
                'sensitive_groups': "People with lung disease, older adults, and children should limit prolonged outdoor exertion and monitor symptoms closely.",
                'children': "It's okay for children to be outdoors, but limit strenuous activities and watch for symptoms like coughing or difficulty breathing.",
                'elderly': "Older adults, especially those with heart or lung conditions, should reduce outdoor activities and monitor their health.",
                'outdoor_workers': "Take more frequent breaks in shaded or indoor areas. Stay well-hydrated and watch for symptoms.",
                'indoor_protection': [
                    "Keep windows closed during peak pollution hours",
                    "Use air purifiers with HEPA filters if available",
                    "Avoid activities that create additional indoor air pollution"
                ],
                'outdoor_protection': [
                    "Consider wearing N95 masks if you're in a sensitive group",
                    "Limit outdoor exercise to times when pollution is lower",
                    "Keep rescue medications handy if you have respiratory conditions",
                    "Choose less-busy routes for commuting to reduce exposure"
                ],
                'health_impacts': "At this level, sensitive individuals may experience respiratory symptoms like coughing or shortness of breath. Research indicates that repeated exposure can contribute to respiratory inflammation and reduced lung function in sensitive groups."
            }
        elif aqi_value <= 200:
            return {
                'general_detailed': "Air quality is unhealthy. Everyone may begin to experience health effects, and members of sensitive groups may experience more serious effects.",
                'general_population': "Everyone should limit prolonged outdoor exertion. Consider rescheduling outdoor activities.",
                'sensitive_groups': "People with heart or lung disease, older adults, and children should avoid prolonged outdoor exertion and stay indoors when possible.",
                'children': "Children should reduce outdoor activities, especially during peak pollution hours. School outdoor activities should be moved indoors.",
                'elderly': "Older adults should stay indoors with windows closed and air purifiers running if available.",
                'outdoor_workers': "Reduce strenuous work, take frequent breaks indoors, and wear protective masks when possible.",
                'indoor_protection': [
                    "Keep all windows and doors closed",
                    "Use air purifiers with HEPA filters in main living areas",
                    "Avoid burning candles or using gas stoves",
                    "Consider using a humidity-controlled air conditioner",
                    "Damp-mop surfaces to reduce settled particles"
                ],
                'outdoor_protection': [
                    "Wear N95 masks when outdoors",
                    "Minimize time spent outdoors, especially during exercise",
                    "Use vehicles with cabin air filters set to recirculate",
                    "Carry any needed medications",
                    "Shower and change clothes after returning indoors"
                ],
                'health_impacts': "Unhealthy air quality can cause respiratory irritation, coughing, shortness of breath, and aggravate existing heart and lung conditions. Research shows that exposure at these levels can cause measurable lung function decreases and inflammatory responses."
            }
        elif aqi_value <= 300:
            return {
                'general_detailed': "Air quality is very unhealthy. Health alert: The risk of health effects is increased for everyone. People should avoid outdoor activities.",
                'general_population': "Avoid all outdoor physical activities. Stay indoors with windows closed and air purifiers running if available.",
                'sensitive_groups': "People with heart or lung disease, older adults, children, and pregnant women should strictly avoid outdoor exposure.",
                'children': "Keep children indoors. All outdoor school activities should be cancelled or moved indoors.",
                'elderly': "Elderly individuals should strictly remain indoors with air filtration. Consider checking in on elderly neighbors.",
                'outdoor_workers': "If possible, move work indoors or reschedule. If outdoor work is mandatory, wear proper respiratory protection and take frequent indoor breaks.",
                'indoor_protection': [
                    "Stay indoors with windows and doors sealed",
                    "Run air purifiers with HEPA filters on highest setting",
                    "Create a clean air room if whole-house filtration isn't available",
                    "Change HVAC filters to highest efficiency possible",
                    "Use wet cleaning methods for dust and avoid vacuuming",
                    "Consider using an N95 mask even indoors if air filtration is poor"
                ],
                'outdoor_protection': [
                    "Avoid all unnecessary outdoor activities",
                    "Wear N95 or preferably N99 masks for any outdoor exposure",
                    "Use eye protection outdoors to reduce eye irritation",
                    "Shower immediately after returning indoors",
                    "Wash clothes exposed to outdoor air separately",
                    "Keep all vehicle windows closed with air on recirculate"
                ],
                'health_impacts': "Very unhealthy air quality can cause significant respiratory distress, aggravate heart and lung disease, and reduce exercise tolerance in healthy individuals. Research links exposure at these levels to increased emergency room visits and negative cardiovascular effects even in healthy people."
            }
        else:
            return {
                'general_detailed': "Air quality is hazardous. Health warning of emergency conditions: everyone is more likely to be affected and should take precautions.",
                'general_population': "Everyone should avoid all physical activity outdoors. If possible, remain indoors with air filtration.",
                'sensitive_groups': "Extremely dangerous conditions for sensitive individuals. Stay indoors with filtered air and minimize physical activity of any kind.",
                'children': "Keep children strictly indoors with activities that don't require physical exertion. Schools should consider closures.",
                'elderly': "Dangerous conditions for elderly. Remain indoors, use air filtration, and monitor for any health changes that may require medical attention.",
                'outdoor_workers': "Outdoor work should be suspended if possible. If critical work must continue, use highest level of respiratory protection available.",
                'indoor_protection': [
                    "Remain indoors with all windows and doors sealed",
                    "Create a clean air shelter in one room with extra sealing and filtration",
                    "Run HEPA air purifiers continuously",
                    "Seal gaps under doors and around windows if possible",
                    "Avoid any activities that generate indoor air pollution",
                    "Consider using N95 masks even indoors if adequate filtration is not available",
                    "Minimize physical activity to reduce breathing rate"
                ],
                'outdoor_protection': [
                    "Avoid all outdoor activity if possible",
                    "If outdoors is unavoidable, wear N99 or N100 respirators",
                    "Cover all exposed skin if possible",
                    "Use sealed goggles to protect eyes",
                    "Keep outdoor exposure as brief as possible",
                    "Shower and change clothes immediately upon returning indoors",
                    "Consider temporary relocation if conditions persist"
                ],
                'health_impacts': "Hazardous air quality presents emergency health conditions. Exposure can cause serious aggravation of heart or lung disease and premature mortality in people with cardiopulmonary disease and older adults. Healthy people will experience adverse respiratory and cardiovascular effects. Research shows significantly increased hospital admissions during these pollution levels."
            }
