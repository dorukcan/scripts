if (!String.prototype.format) {
    String.prototype.format = function () {
        var args = arguments;

        if (typeof arguments[0] === "object" && arguments.length === 1) {
            args = arguments[0];
        }

        return this.replace(/{(\d+)}/g, function (match, index) {
            return typeof args[index] !== 'undefined'
                ? args[index]
                : match;
        });
    };
}

var c0l0r = {
    baseColor: null,
    palette: {
        generate: function (startColor, interval) {
            c0l0r.baseColor = c0l0r.lib.hex(startColor);

            var rgb = c0l0r.lib.hexToRgb(c0l0r.baseColor);
            var hsl = c0l0r.lib.rgbToHsl(rgb);

            return [{
                "name": "rgb-red-green",
                "data": this.compose(rgb, interval, "red", "green")
            }, {
                "name": "rgb-red-blue",
                "data": this.compose(rgb, interval, "red", "blue")
            }, {
                "name": "rgb-green-blue",
                "data": this.compose(rgb, interval, "green", "blue")
            }, {
                "name": "hsl-hue-lightness",
                "data": this.compose(hsl, interval, "hue", "lightness")
            }, {
                "name": "hsl-hue-saturation",
                "data": this.compose(hsl, interval, "hue", "saturation")
            }, {
                "name": "hsl-lightness-saturation",
                "data": this.compose(hsl, interval, "lightness", "saturation")
            }];
        },
        compose: function (color, interval, field1, field2) {
            var result = [];
            var i, j, field1Changed, field2Changed, row;
            var type = color["type"];

            for (i = 0; i < interval; i++) {
                row = [];
                field1Changed = this.changeField[type][field1](color, 100 / interval * i);

                for (j = 0; j < interval; j++) {
                    field2Changed = this.changeField[type][field2](field1Changed, 100 / interval * j);
                    //row.push(c0l0r.helper.colorToStr(field2Changed));
                    row.push(field2Changed);
                }

                result.push(row);
            }

            return result;
        },
        changeField: {
            rgb: {
                red: function (color, percent) {
                    var temp = c0l0r.helper.cloneColor(color);
                    temp["r"] = Math.floor(temp["r"] + 255 * percent / 100) % 255;

                    return temp;
                },
                green: function (color, percent) {
                    var temp = c0l0r.helper.cloneColor(color);
                    temp["g"] = Math.floor(temp["g"] + 255 * percent / 100) % 255;

                    return temp;
                },
                blue: function (color, percent) {
                    var temp = c0l0r.helper.cloneColor(color);
                    temp["b"] = Math.floor(temp["b"] + 255 * percent / 100) % 255;

                    return temp;
                }
            },
            hsl: {
                hue: function (color, percent) {
                    var temp = c0l0r.helper.cloneColor(color);
                    temp["h"] = (temp["h"] + 360 * percent / 100) % 360;

                    return temp;
                },
                saturation: function (color, percent) {
                    var temp = c0l0r.helper.cloneColor(color);
                    temp["s"] = (temp["s"] + percent) % 100;

                    return temp;
                },
                lightness: function (color, percent) {
                    var temp = c0l0r.helper.cloneColor(color);
                    temp["l"] = (temp["l"] + percent) % 100;

                    return temp;
                }
            }
        },
        show: function (palette) {
            //console.log(palette);

            var spacesTemplate = "[{0}] %c                                                                             ";
            var colorTemplate = "background: linear-gradient(to right, {0} 0, {1} 20%, {2} 40%, {3} 60%, {4} 80%)";

            palette.forEach(function (scheme) {
                console.log(scheme["name"]);
                scheme["data"].forEach(function (row, i) {
                    console.log(spacesTemplate.format(i), colorTemplate.format(row));
                });
                console.log("--------------");
            });
        }
    },

    helper: {
        showColor: function (value, debug) {
            debug = typeof debug !== 'undefined' ? debug : true;

            var outputItem, outputStr;

            if (debug === true) {
                // konsola yaz
                console.log(value);

                // container oluştur
                outputItem = document.body.appendChild(document.createElement('pre'));

                // görseli göster
                outputItem.innerHTML += c0l0r.helper.renderColor(value);

                // datayı göster
                outputStr = JSON.stringify(value, null, 4);
                outputItem.innerHTML += this.syntaxHighlight(outputStr) + "<br /><br />";
            }
            else {
                // container oluştur
                outputItem = document.body.appendChild(document.createElement('span'));

                // görseli göster
                outputItem.innerHTML += c0l0r.helper.renderColor(value);
            }
        },
        showPalette: function (palette) {
            var div;

            palette.forEach(function (scheme) {
                scheme["data"].forEach(function (row) {
                    div = document.createElement("div");
                    row.forEach(function(color){
                        div.innerHTML += c0l0r.helper.renderColor(color);
                    });
                    document.body.appendChild(div);
                });
                document.body.innerHTML += "<br /><br />";
            });

        },
        renderColor: function(value){
            var colorStr = c0l0r.helper.colorToStr(value);
            return c0l0r.helper.createHtmlBlock(colorStr);
        },
        createHtmlBlock: function (bgColor) {
            var block = document.createElement('span');

            var style = "background-color: {0};".format(bgColor);
            style += "width: 50px; height: 50px; display: inline-block; margin-right: 5px; margin-bottom: 5px;";

            block.setAttribute("style", style);

            return block.outerHTML;
        },
        syntaxHighlight: function (json) {
            json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
                var cls = 'number';
                if (/^"/.test(match)) {
                    if (/:$/.test(match)) {
                        cls = 'key';
                    } else {
                        cls = 'string';
                    }
                } else if (/true|false/.test(match)) {
                    cls = 'boolean';
                } else if (/null/.test(match)) {
                    cls = 'null';
                }
                return '<span class="' + cls + '">' + match + '</span>';
            });
        },
        colorToStr: function (color) {
            if (color["type"] === "hex") {
                return color["color"];
            }
            else if (color["type"] === "rgb") {
                return "rgb({0}, {1}, {2})".format(color["r"], color["g"], color["b"]);
            }
            else if (color["type"] === "hsl") {
                return "hsl({0}, {1}%, {2}%)".format(color["h"], color["s"], color["l"]);
            }
        },
        cloneColor: function (color) {
            return JSON.parse(JSON.stringify(color));
        }
    },

    lib: {
        hex: function (color) {
            return {
                "type": "hex",
                "color": color
            }
        },
        hexToRgb: function (hex) {
            hex = hex["color"];

            var hexToR = function (h) {
                return parseInt((cutHex(h)).substring(0, 2), 16)
            };
            var hexToG = function (h) {
                return parseInt((cutHex(h)).substring(2, 4), 16)
            };
            var hexToB = function (h) {
                return parseInt((cutHex(h)).substring(4, 6), 16)
            };
            var cutHex = function (h) {
                return (h.charAt(0) === "#") ? h.substring(1, 7) : h
            };

            return {
                "type": "rgb",
                "r": hexToR(hex),
                "g": hexToG(hex),
                "b": hexToB(hex)
            };
        },
        rgbToHsl: function (rgbInput) {
            var min, max, i, l, s, maxcolor, h, rgb = [];
            rgb[0] = rgbInput["r"] / 255;
            rgb[1] = rgbInput["g"] / 255;
            rgb[2] = rgbInput["b"] / 255;
            min = rgb[0];
            max = rgb[0];
            maxcolor = 0;
            for (i = 0; i < rgb.length - 1; i++) {
                if (rgb[i + 1] <= min) {
                    min = rgb[i + 1];
                }
                if (rgb[i + 1] >= max) {
                    max = rgb[i + 1];
                    maxcolor = i + 1;
                }
            }
            if (maxcolor === 0) {
                h = (rgb[1] - rgb[2]) / (max - min);
            }
            if (maxcolor === 1) {
                h = 2 + (rgb[2] - rgb[0]) / (max - min);
            }
            if (maxcolor === 2) {
                h = 4 + (rgb[0] - rgb[1]) / (max - min);
            }
            if (isNaN(h)) {
                h = 0;
            }
            h = h * 60;
            if (h < 0) {
                h = h + 360;
            }
            l = (min + max) / 2;
            if (min === max) {
                s = 0;
            } else {
                if (l < 0.5) {
                    s = (max - min) / (max + min);
                } else {
                    s = (max - min) / (2 - max - min);
                }
            }

            return {
                "type": "hsl",
                "h": h,
                "s": s * 100,
                "l": l * 100
            };
        }
    }
};

var palette = c0l0r.palette.generate("#f5f5f5", 10);
c0l0r.helper.showColor(c0l0r.baseColor, true);
c0l0r.helper.showPalette(palette);
