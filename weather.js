var weather = {
    load: function () {
        var url = 'http://api.openweathermap.org/data/2.5/forecast';
        url += '?id=745044';
        url += '&units=metric';
        url += '&lang=tr';
        url += '&APPID=a47c752dd4605f7b9b283d6b9bedc5fb';

        dashboard.helper.ajax(url, function (responseText) {
            weather.rawData = responseText;
            weather.cleanData = weather.clean();
            weather.draw.draw();
        });
    },
    clean: function () {
        var temp,
            timestamp;
        // var daysTr = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'];

        var rawData = JSON.parse(this.rawData);
        var cleanData = {
            city: rawData.city,
            list: []
        };

        rawData.list.forEach(function (data) {
            timestamp = new Date(data.dt * 1000);

            temp = {
                timestamp: timestamp,
                description: data.weather[0].description,
                type: data.weather[0].main,
                icon_url: 'http://openweathermap.org/img/w/' + data.weather[0].icon + '.png',
                temp: data.main.temp,
                clouds: data.clouds.all,
                wind: data.wind.speed,
                rain: data.rain === undefined ? 0 : data.rain['3h']
            };
            cleanData.list.push(temp);
        });

        return cleanData;
    },
    draw: {
        draw: function () {
            this.defineComponents();
            this.addAxises();
            this.addLine();
            this.fillArea();
            this.putLabelAndPoint();
            this.addRainBlocks();
            this.addIcon();
            this.seperateIcons();
            this.addImage();
        },
        defineComponents: function () {
            // Cut data for 30 hours period
            this.dataset = weather.cleanData.list.slice(0, 10);
            console.log(this.dataset);

            // Set dimensions
            this.margin = {
                top: 30,
                right: 40,
                bottom: 30,
                left: 40
            };
            this.width = window.innerWidth - this.margin.left - this.margin.right - 40;
            this.height = 270 - this.margin.top - this.margin.bottom;

            // Create svg and base
            this.svg = d3.select(".weather-container")
                .append("svg")
                .attr("width", this.width + this.margin.left + this.margin.right)
                .attr("height", this.height + this.margin.top + this.margin.bottom)
                .append("g")
                .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");

            // Set scales
            this.timeScale = d3.scaleTime()
                .range([0, this.width])
                .domain(d3.extent(this.dataset, function (d) {
                    return d.timestamp;
                }));

            this.tempScale = d3.scaleLinear()
                .range([this.height, 0])
                .domain([0, d3.max(this.dataset, function (d) {
                    return d.temp;
                })]);
        },
        addAxises: function () {
            var xAxis = d3.axisBottom(this.timeScale).tickFormat(d3.timeFormat('%H:%M'));
            this.svg.append("g")
                .attr("transform", "translate(0," + this.height + ")")
                .call(xAxis);

            var yAxis = d3.axisLeft(this.tempScale);
            this.svg.append("g")
                .call(yAxis);
        },
        addLine: function () {
            var that = this;
            this.svg.append("path")
                .datum(this.dataset)
                .style('stroke', '#ffa500')
                .style('stroke-width', '3')
                .style('fill', 'none')
                .attr("d", d3.line()
                    .curve(d3.curveCardinal)
                    .x(function (d) {
                        return that.timeScale(d.timestamp);
                    })
                    .y(function (d) {
                        return that.tempScale(d.temp);
                    })
                );
        },
        putLabelAndPoint: function () {
            var that = this;

            var tempPoint = this.svg.selectAll(".temp-point")
                .data(this.dataset)
                .enter();

            tempPoint.append("circle")
                .attr("fill", "#ffa500")
                .attr("stroke", "#ffa500")
                .attr("stroke-width", "2")
                .attr("cx", function (d) {
                    return that.timeScale(d.timestamp)
                })
                .attr("cy", function (d) {
                    return that.tempScale(d.temp);
                })
                .attr("r", 3)
                .on("mouseover", function (d) {
                    d3.select(this).attr("r", 4);
                })
                .on("mouseout", function (d) {
                    d3.select(this).attr("r", 3);
                });

            tempPoint.append("text")
                .attr("x", function (d) {
                    return that.timeScale(d.timestamp)
                })
                .attr("y", function (d) {
                    return that.tempScale(d.temp);
                })
                .attr('dy', "-10px")
                .style("text-anchor", "middle")
                .text(function (d) {
                    return d.temp + "°";
                });
        },
        fillArea: function () {
            var that = this;
            this.svg.append("path")
                .datum(this.dataset)
                .attr("fill", "#fffbc1")
                .attr("stroke-width", "0")
                .attr("opacity", ".5")
                .attr("d", d3.area()
                    .curve(d3.curveCardinal)
                    .x(function (d) {
                        return that.timeScale(d.timestamp);
                    })
                    .y0(this.height)
                    .y1(function (d) {
                        return that.tempScale(d.temp);
                    })
                );
        },
        addRainBlocks: function () {
            var that = this;
            this.svg.selectAll(".rainBlock")
                .data(this.dataset)
                .enter()
                .append("rect")
                .attr("fill", "#3590df")
                .attr("stroke-width", "0")
                .attr("width", that.width / (that.dataset.length - 1))
                .attr("height", function (d) {
                    if (d.rain && d.rain !== 0) {
                        var rain = (d.rain) ? d.rain : 0;
                        return (that.height * rain) / 10;
                    }
                    else {
                        return 0;
                    }
                })
                .attr("x", function (d) {
                    return that.timeScale(d.timestamp);
                })
                .attr("y", function (d) {
                    return that.height - d3.select(this).attr("height");
                });
        },
        addIcon: function () {
            var that = this;
            this.svg.selectAll(".icon")
                .data(that.dataset)
                .enter()
                .append('image')
                .attr('xlink:href', function (d) {
                    return d.icon_url;
                })
                .attr('width', '50')
                .attr('height', '50')
                .attr('x', function (d) {
                    return that.timeScale(d.timestamp) + that.width / (that.dataset.length - 1) / 2 - d3.select(this).attr("width") / 2;
                })
                .attr('y', function (d) {
                    return that.tempScale(d.temp / 2) - d3.select(this).attr("height") / 2;
                });
        },
        seperateIcons: function () {
            var that = this;

            this.svg.selectAll(".seperate")
                .data(this.dataset)
                .enter()
                .append("line")
                .attr('stroke', '#ffd060')
                .attr('stroke-width', '2')
                .attr("stroke-dasharray", "15,30")
                .attr("x1", function (d) {
                    return that.timeScale(d.timestamp);
                })
                .attr("y1", this.height)
                .attr("x2", function (d) {
                    return that.timeScale(d.timestamp);
                })
                .attr("y2", function (d) {
                    return that.tempScale(d.temp);
                });
        },
        addImage: function () {
            var that = this;

            this.svg.selectAll(".background-image")
                .data(that.dataset)
                .enter()
                .append('image')
                .attr('xlink:href', function (d) {
                    var url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search';
                    url += '&api_key=570fe7481680c7aa6b6fb9e190a8820e';
                    url += '&format=json';
                    url += '&nojsoncallback=1';
                    url += '&extras=url_t,url_q';
                    url += '&per_page=50';
                    url += '&sort=relevance';
                    url += '&privacy_filter=1';
                    url += '&content_type=1';
                    url += '&media=photos'; // videos da olabilir
                    url += '&text=' + weather.cleanData.city.name + " " + d.type;

                    var image_url = null;
                    dashboard.helper.ajax(url, function (responseText) {
                        var responseJson = JSON.parse(responseText);
                        image_url = responseJson["photos"]["photo"][0]["url_q"];
                    });

                    return image_url;
                })
                .attr('width', '100')
                .attr('height', '100')
                .attr('x', function (d) {
                    return that.timeScale(d.timestamp);
                })
                .attr('y', function (d) {
                    return that.height;
                });
        }
    }
};

weather.load();