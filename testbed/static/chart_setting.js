window.onload=function()
{//w ww . java  2  s.  c om
// Show tooltips always even the stats are zero
Chart.pluginService.register({
beforeRender: function(chart) {
if (chart.config.options.showAllTooltips) {
  // create an array of tooltips
  // we can't use the chart tooltip because there is only one tooltip per chart
  chart.pluginTooltips = [];
  chart.config.data.datasets.forEach(function(dataset, i) {
    chart.getDatasetMeta(i).data.forEach(function(sector, j) {
      chart.pluginTooltips.push(new Chart.Tooltip({
        _chart: chart.chart,
        _chartInstance: chart,
        _data: chart.data,
        _options: chart.options.tooltips,
        _active: [sector]
      }, chart));
    });
  });
  // turn off normal tooltips
  chart.options.tooltips.enabled = false;
}
},
afterDraw: function(chart, easing) {
if (chart.config.options.showAllTooltips) {
  // we don't want the permanent tooltips to animate, so don't do anything till the animation runs atleast once
  if (!chart.allTooltipsOnce) {
    if (easing !== 1)
      return;
    chart.allTooltipsOnce = true;
  }
  // turn on tooltips
  chart.options.tooltips.enabled = true;
  Chart.helpers.each(chart.pluginTooltips, function(tooltip) {
    tooltip.initialize();
    tooltip.update();
    // we don't actually need this since we are not animating tooltips
    tooltip.pivot();
    tooltip.transition(easing).draw();
  });
  chart.options.tooltips.enabled = false;
}
}
});
// Show tooltips always even the stats are zero
var canvas = $('#myCanvas2').get(0).getContext('2d');
var doughnutChart = new Chart(canvas, {
type: 'doughnut',
data: {
labels: [
  "Success",
  "Failure"
],
datasets: [{
  data: [45, 9],
  backgroundColor: [
    "#1ABC9C",
    "#566573"
  ],
  hoverBackgroundColor: [
    "#148F77",
    "#273746"
  ]
}]
},
options: {
// In options, just use the following line to show all the tooltips
showAllTooltips: true
}
});
}