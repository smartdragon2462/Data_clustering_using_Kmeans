(function() {
//    window.alert("Hello");
    $('.add-file-button').css('display', 'block');
    $('.loaded-file-info').css('display', 'none');

    $('.add-file-button').on("click",function(){
      $('#upload')[0].click();
      //post code
    });

    $('input[type="file"]').change(function(e){
        var fileName = e.target.files[0].name;
        var fileSize = e.target.files[0].size;
        $('.add-file-button').css('display', 'none');
        $('.loaded-file-info').css('display', 'block');
        $(".file-name").html(fileName);
        $(".file-size").html( Math.ceil(fileSize/1000)+"kb size");

        var formdata = new FormData;

        formdata.append('file', e.target.files[0]);
        jQuery.ajax({
            url: 'http://localhost:5000/upload',
            data: formdata,
            cache: false,
            contentType: false,
            processData: false,
            method: 'POST',
//            type: 'POST', // For jQuery < 1.9
            success: function(data){
                $('#right_container').empty();
                $('#right_container').html(data);
            }
        });
    });

}).call(this);

function run() {
    var cohorts = $('#cohor_count').val();
    $('.loading-wrapper').show();
    jQuery.ajax({
        url: 'http://localhost:5000/result',
//        url: 'http://localhost:5000/result',
        type: 'post',
        data: {cohorts: cohorts},
        success: function(data){
            var table = data.split(';')[0];
            var clusters = JSON.parse(data.split(';')[1]);

            console.log(clusters[0][2]);
            $('#result_table').empty();
            $('#result_table').html(table);
            $('#result_title').html("Results");
            setTimeout(function() {
                $('.loading-wrapper').hide();
            }, 500);

            $('#chart-container').empty();

            for(var i=0; i<cohorts; i++) {
                $('#chart-container').append('<div id="container' + i + '" class="chart-item"></div>');

                var total=0;
                for(var a in clusters[i]) { total += a; }

                Highcharts.chart('container' + i, {
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false,
                        type: 'pie'
                    },
                    title: {
                        text: 'Cohort '+(i+1)
                    },
                    tooltip: {
                        pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                    },
                    plotOptions: {
                        pie: {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: false
                            },
                            showInLegend: true
                        }
                    },
                    series: [{
                        name: 'Cohort '+(i+1),
                        colorByPoint: true,
                        data: [{
                            name: 'Age',
                            y: clusters[i][0]/total,
//                            sliced: true,
//                            selected: true
                        }, {
                            name: 'EmployeeNumber',
                            y: clusters[i][1]/total
                        }, {
                            name: 'Gender',
                            y: clusters[i][2]/total
                        }, {
                            name: 'JobLevel',
                            y: clusters[i][3]/total
                        }, {
                            name: 'MaritalStatus',
                            y: clusters[i][4]/total
                        }, {
                            name: 'MonthlyIncome',
                            y: clusters[i][5]/total
                        }, {
                            name: 'TotalWorkingYears',
                            y: clusters[i][6]/total
                        }]
                    }]
                });
            }


        }
    });
}

function getCluster(id) {
//    $('#modal-text').html('clicked ' + id + ' cluster');

    jQuery.ajax({
        url: 'http://localhost:5000/cluster',
//        url: 'http://localhost:5000/cluster',
        type: 'post',
        data: {clusterID: id},
        success: function(data){
            $('#modal-text').empty();
            $('#modal-text').html(data);
//            setTimeout(function() {
//                $('.loading-wrapper').hide();
//            }, 500);

        }
    });

}
