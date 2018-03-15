'use strict';

W.ns('W.pages.business');

W.pages.business.Analytics = Class.extend({

    init: function init() {
        this.configureDatePicker();
    },
    configureDatePicker: function(){
        $("#update").on("click", function(){
            window.location.href = window.location.pathname + "?from_date={1}&to_date={0}".format($("#to").val(), $("#from").val());
        });

        Date.prototype.addDays = function(days) {
          var dat = new Date(this.valueOf());
          dat.setDate(dat.getDate() + days);
          return dat;
        }

        var from_date = new Date(),
            from = $( "#from" ).datepicker({
                  dateFormat: 'yy-mm-dd',
                  defaultDate: "+1w",
                  changeMonth: true,
                  numberOfMonths: 1
                }).on( "change", function() {
                    to.datepicker( "option", "minDate", getDate( this ) );
                }).datepicker("setDate", from_date.addDays(-7)),

            to = $( "#to" ).datepicker({
                dateFormat: 'yy-mm-dd',
                changeMonth: true,
                numberOfMonths: 1
                }).on( "change", function() {
                    from.datepicker( "option", "maxDate", getDate( this ) );
                }).datepicker("setDate", new Date());
     
        function getDate( element ) {
            var date;

            try {
                date = $.datepicker.parseDate("yyyy-mm-dd", element.value );
            } catch( error ) {
                date = null;
            }

            return date;
        }

        if(window.location.href.indexOf("?") > -1){
            var qs = W.qs(window.location.href);

            if(qs.to){
                $("#to").val(qs.to_date);
                $("#from").val(qs.from_date);
            }

        }
    },

    parseData: function (data) {
        if (data && typeof data === 'object') {
            return data.map(function (obj) {
                return [obj.day, obj.count]
            })
        }
    },

    drawBizLookupChart: function(data){
        Highcharts.chart('biz-lookup-chart', {
            title: {
                text: 'Dispensary Page Views using Business Lookup'
            },
            subtitle: {
                text: 'Shows how many people viewed your dispensary page from our dispensary lookup tool'
            },
            xAxis: {
                type:"category",
                labels: {
                   rotation: 20
                } 
            },
            yAxis: {
                title: {
                    text: 'Views'
                },
                tickInterval: 1                
            },
            series: [{
                name: 'Views',
                data: this.parseData(data || [])
            }],
            responsive: {
                rules: [{
                    condition: {
                        maxWidth: 500
                    },
                    chartOptions: {
                        legend: {
                            layout: 'horizontal',
                            align: 'center',
                            verticalAlign: 'bottom'
                        }
                    }
                }]
            }

        });        
    },
    drawSearchChart: function(data){
        Highcharts.chart('search-chart', {
            title: {
                text: 'Dispensary Page Views using Available At'
            },
            subtitle: {
                text: 'Shows how many people viewed your dispensary page from using our Available At feature on Strain pages'
            },
            xAxis: {
                type:"category",
                labels: {
                   rotation: 20,
                }
            },
            yAxis: {
                title: {
                    text: 'Views'
                },
                tickInterval: 1
            },
            series: [{
                name: 'Views',
                data: this.parseData(data || [])
            }],
            responsive: {
                rules: [{
                    condition: {
                        maxWidth: 500
                    },
                    chartOptions: {
                        legend: {
                            layout: 'horizontal',
                            align: 'center',
                            verticalAlign: 'bottom'
                        }
                    }
                }]
            }

        });        
    },

    drawUpdateRequestChart: function(data){
        Highcharts.chart('update-request-chart', {
            title: {
                text: 'Update Requests'
            },
            subtitle: {
                text: 'Shows update requests count'
            },
            xAxis: {
                type:"category",
                labels: {
                   rotation: 20
                }
            },
            yAxis: {
                title: {
                    text: 'Views'
                },
                tickInterval: 1
            },
            series: [{
                name: 'Views',
                data: this.parseData(data || [])
            }],
            responsive: {
                rules: [{
                    condition: {
                        maxWidth: 500
                    },
                    chartOptions: {
                        legend: {
                            layout: 'horizontal',
                            align: 'center',
                            verticalAlign: 'bottom'
                        }
                    }
                }]
            }

        });
    }

});
