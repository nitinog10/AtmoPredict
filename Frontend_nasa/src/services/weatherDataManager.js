class WeatherDataManager {
    constructor() {
        this.continentData = {};
        this.hemisphereData = {};
        this.locationMapping = null;
        this.loaded = false;
    }

    async loadData() {
        try {
            // Load location mapping
            const mappingResponse = await fetch('/data/location_mapping.json');
            this.locationMapping = await mappingResponse.json();

            // Load hemisphere data
            const northernResponse = await fetch('/data/hemispheres/northern_hemisphere.json');
            const southernResponse = await fetch('/data/hemispheres/southern_hemisphere.json');
            
            this.hemisphereData.northern = await northernResponse.json();
            this.hemisphereData.southern = await southernResponse.json();

            // Load continent data
            const continents = ['asia', 'europe', 'north_america', 'south_america', 'africa', 'australia', 'antarctica'];
            
            for (const continent of continents) {
                try {
                    const response = await fetch(`/data/continents/${continent}.json`);
                    this.continentData[continent] = await response.json();
                } catch (error) {
                    console.warn(`Failed to load ${continent} data:`, error);
                }
            }

            this.loaded = true;
            console.log('Weather data loaded successfully');
        } catch (error) {
            console.error('Failed to load weather data:', error);
            this.loaded = false;
        }
    }

    getRegionFromCoordinates(lat, lon) {
        if (!this.loaded || !this.locationMapping) {
            return { continent: 'asia', hemisphere: 'northern' };
        }

        const hemisphere = lat >= 0 ? 'northern' : 'southern';

        for (const [continentName, region] of Object.entries(this.locationMapping.coordinate_regions)) {
            const latInRange = lat >= region.lat_range[0] && lat <= region.lat_range[1];
            const lonInRange = lon >= region.lon_range[0] && lon <= region.lon_range[1];
            
            if (latInRange && lonInRange) {
                return {
                    continent: continentName,
                    hemisphere: region.hemisphere === 'Mixed' ? hemisphere : region.hemisphere.toLowerCase(),
                    continentFile: region.continent_file
                };
            }
        }

        return { continent: null, hemisphere: hemisphere };
    }

    getSixMonthForecast(lat, lon) {
        const region = this.getRegionFromCoordinates(lat, lon);
        
        if (region.continent && this.continentData[region.continent]) {
            return this.generateForecastFromContinent(region.continent, lat, lon);
        }
        
        return this.generateForecastFromHemisphere(region.hemisphere, lat, lon);
    }

    getCurrentMonthIndex() {
        const currentDate = new Date();
        const currentMonth = currentDate.getMonth();
        return currentMonth + 1;
    }

    generateForecastFromContinent(continent, lat, lon) {
        const data = this.continentData[continent];
        if (!data) return this.getDefaultForecast();

        const forecast = [];
        const currentMonth = this.getCurrentMonthIndex();
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        
        for (let i = 0; i < 6; i++) {
            let monthIndex = (currentMonth + i) % 12;
            if (monthIndex === 0) monthIndex = 12;
            
            const patternIndex = (i % 6) + 1;
            const monthData = data.six_month_patterns[`month_${patternIndex}`];
            
            if (!monthData) continue;

            const latVariation = Math.sin(lat * Math.PI / 180) * 0.1;
            const lonVariation = Math.cos(lon * Math.PI / 180) * 0.1;
            const variation = latVariation + lonVariation;

            const futureDate = new Date();
            futureDate.setMonth(futureDate.getMonth() + i);

            forecast.push({
                month: monthNames[monthIndex - 1],
                monthNumber: monthIndex,
                date: futureDate.toISOString().slice(0, 10),
                temperature: {
                    avg: Math.round((monthData.temperature.avg + variation * 5) * 10) / 10,
                    min: Math.round((monthData.temperature.min + variation * 3) * 10) / 10,
                    max: Math.round((monthData.temperature.max + variation * 7) * 10) / 10
                },
                humidity: {
                    avg: Math.round(Math.max(10, Math.min(95, monthData.humidity.avg + variation * 10)))
                },
                precipitation: {
                    avg: Math.round(Math.max(0, monthData.precipitation.avg + variation * 20))
                },
                wind_speed: {
                    avg: Math.round(Math.max(1, monthData.wind_speed.avg + variation * 5) * 10) / 10
                },
                extreme_weather_risk: {
                    very_hot: Math.max(0, Math.min(0.1, (monthData.extreme_weather_risk.very_hot + variation * 0.1) / 10)),
                    very_cold: Math.max(0, Math.min(0.1, (monthData.extreme_weather_risk.very_cold + variation * 0.1) / 10)),
                    very_windy: Math.max(0, Math.min(0.1, (monthData.extreme_weather_risk.very_windy + variation * 0.1) / 10)),
                    very_wet: Math.max(0, Math.min(0.1, (monthData.extreme_weather_risk.very_wet + variation * 0.1) / 10)),
                    very_uncomfortable: Math.max(0, Math.min(0.1, (monthData.extreme_weather_risk.very_uncomfortable + variation * 0.1) / 10))
                },
                data_source: `🌍 ${data.continent} Climate Pattern`,
                confidence: Math.round((0.75 + Math.random() * 0.2) * 100) / 100
            });
        }

        return forecast;
    }

    generateForecastFromHemisphere(hemisphere, lat, lon) {
        const data = this.hemisphereData[hemisphere];
        if (!data) return this.getDefaultForecast();

        const forecast = [];
        const currentMonth = this.getCurrentMonthIndex();
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        
        for (let i = 0; i < 6; i++) {
            let monthIndex = (currentMonth + i) % 12;
            if (monthIndex === 0) monthIndex = 12;
            
            const patternIndex = (i % 6) + 1;
            const monthData = data.six_month_patterns[`month_${patternIndex}`];
            
            if (!monthData) continue;

            const latVariation = Math.sin(lat * Math.PI / 180) * 0.15;
            const lonVariation = Math.cos(lon * Math.PI / 180) * 0.15;
            const variation = latVariation + lonVariation;

            const futureDate = new Date();
            futureDate.setMonth(futureDate.getMonth() + i);

            forecast.push({
                month: monthNames[monthIndex - 1],
                monthNumber: monthIndex,
                date: futureDate.toISOString().slice(0, 10),
                temperature: {
                    avg: Math.round((monthData.global_temp.avg + variation * 8) * 10) / 10,
                    min: Math.round((monthData.global_temp.range[0] + variation * 5) * 10) / 10,
                    max: Math.round((monthData.global_temp.range[1] + variation * 10) * 10) / 10
                },
                humidity: {
                    avg: Math.round(Math.max(10, Math.min(95, monthData.global_humidity.avg + variation * 12)))
                },
                precipitation: {
                    avg: Math.round(Math.max(0, monthData.global_precipitation.avg + variation * 30))
                },
                wind_speed: {
                    avg: Math.round(Math.max(1, monthData.global_wind.avg + variation * 8) * 10) / 10
                },
                extreme_weather_risk: Object.fromEntries(
                    Object.entries(monthData.extreme_weather_trends).map(([key, value]) => [key, value / 10])
                ),
                data_source: `🌐 ${hemisphere.charAt(0).toUpperCase() + hemisphere.slice(1)} Hemisphere`,
                confidence: Math.round((0.65 + Math.random() * 0.25) * 100) / 100
            });
        }

        return forecast;
    }

    getDefaultForecast() {
        const forecast = [];
        const currentMonth = this.getCurrentMonthIndex();
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        
        for (let i = 0; i < 6; i++) {
            let monthIndex = (currentMonth + i) % 12;
            if (monthIndex === 0) monthIndex = 12;
            
            const futureDate = new Date();
            futureDate.setMonth(futureDate.getMonth() + i);
            
            forecast.push({
                month: monthNames[monthIndex - 1],
                monthNumber: monthIndex,
                date: futureDate.toISOString().slice(0, 10),
                temperature: { avg: 20.0, min: 10.0, max: 30.0 },
                humidity: { avg: 60 },
                precipitation: { avg: 100 },
                wind_speed: { avg: 15.0 },
                extreme_weather_risk: {
                    very_hot: 0.015, very_cold: 0.010, very_windy: 0.010,
                    very_wet: 0.020, very_uncomfortable: 0.012
                },
                data_source: '🌍 Global Climate Model',
                confidence: 0.60
            });
        }
        return forecast;
    }

    getNearestCity(lat, lon) {
        let nearestCity = null;
        let minDistance = Infinity;

        for (const [continentName, continentData] of Object.entries(this.continentData)) {
            if (continentData.representative_cities) {
                for (const city of continentData.representative_cities) {
                    const distance = this.calculateDistance(lat, lon, city.lat, city.lon);
                    if (distance < minDistance) {
                        minDistance = distance;
                        nearestCity = {
                            ...city,
                            continent: continentName,
                            distance: distance
                        };
                    }
                }
            }
        }

        return nearestCity;
    }

    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
}

export const weatherDataManager = new WeatherDataManager();
