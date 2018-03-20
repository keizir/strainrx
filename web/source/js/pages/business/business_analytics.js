'use strict';

W.ns('W.pages.business');

W.pages.business.Analytics = Class.extend({

    init: function init() {
        this.configureDatePicker();
    },

    configureDatePicker: function(){

        $("#reportrange").on("apply.daterangepicker", function(ev, picker){

            window.location.href = window.location.pathname + "?from_date={1}&to_date={0}".format(
                picker.endDate.format('YYYY-MM-DD'),
                picker.startDate.format('YYYY-MM-DD')
            );
        });

        var start = moment().subtract(7, 'days');
        var end = moment();

        if(window.location.href.indexOf("?") > -1) {
            var qs = W.qs(window.location.href);
            start = moment(qs.from_date) || end;
            end = moment(qs.to_date) || start;
        }

        function cb(start, end) {
            $('#reportrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
        }

        $('#reportrange').daterangepicker({
            startDate: start,
            endDate: end,
            ranges: {
               'Today': [moment(), moment()],
               'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
               'Last 7 Days': [moment().subtract(6, 'days'), moment()],
               'Last 14 Days': [moment().subtract(13, 'days'), moment()],
               'Last 30 Days': [moment().subtract(29, 'days'), moment()],
               'This Month': [moment().startOf('month'), moment().endOf('month')],
               'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            }
        }, cb);

        cb(start, end);
    },

    parseData: function (data) {
        var len = data.length,
            obj, end, start, range = [];

        if (data && typeof data === 'object') {
            for (var i = 0; i < len; i += 1) {
                obj = data[i];
                end = i + 1 < len && moment(data[i + 1].day);
                start = moment(obj.day);
                range.push([obj.day, obj.count]);

                if (end && end.diff(start, 'days') > 1) {
                    // if there are no data between two dates fill skipped dates with zero.
                    for (var j = 1; j < end.diff(start, 'days') - 1; j += 1) {
                        range.push([start.add(1, 'days').format('YYYY-MM-DD'), 0])
                    }
                }
            }
        }
        return range
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
