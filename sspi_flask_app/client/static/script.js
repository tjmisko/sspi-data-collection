async function fetchComparisonData(country1,country2,country3){country_data=await fetch(`/api/v1/query/sspi_main_data_v3?CountryCode=${country1}&CountryCode=${country2}&CountryCode=${country3}`)}
function categoryComparison(chartCanvas,categoryCode,country_data){const chartConfig={type:'bar',data:data,options:{plugins:{title:{display:true,text:'Comparison of Category Scores'},},responsive:true,scales:{x:{stacked:true,},y:{stacked:true}}}};}
$(".data-download-reveal").click(()=>{$(".data-download-form").slideDown();$(".data-download-reveal").slideUp();})
$(".data-download-close").click(()=>{$(".data-download-reveal").slideDown();$(".data-download-form").slideUp();})
async function getStaticData(IndicatorCode){const response=await fetch(`/api/v1/static/indicator/${IndicatorCode}`)
try{return response.json()}catch(error){console.error('Error:',error)}}
async function getDynamicData(IndicatorCode){const response=await fetch(`/api/v1/dynamic/line/${IndicatorCode}`)
try{return response.json()}catch(error){console.error('Error:',error)}}
function initCharts(){const StaticCanvas=document.getElementById('static-chart')
const StaticChart=new Chart(StaticCanvas,{type:'bar',options:{plugins:{legend:{display:false,}},scales:{y:{beginAtZero:true}}}})
const DynamicCanvas=document.getElementById('dynamic-chart')
const DynamicChart=new Chart(DynamicCanvas,{type:'line',options:{plugins:{legend:{display:false,position:'bottom'},layout:{padding:{bottom:50}}},scales:{y:{beginAtZero:true}}}})
return[StaticChart,DynamicChart]}
[StaticChart,DynamicChart]=initCharts()
function doStaticChartUpdate(ChartData,ChartObject){ChartObject.data=ChartData
ChartObject.update()}
function doDynamicChartUpdate(ChartData,ChartObject){ChartObject.data.labels=ChartData.labels
ChartObject.data.datasets=ChartData.data
ChartObject.options.scales=ChartData.scales
ChartObject.options.plugins.title=ChartData.title
ChartObject.update()}
window.onresize=function(){StaticChart.resize()
}
function handleScaleAxis(ChartObject,ScaleByValue){const original_data=ChartObject.data
if(ScaleByValue){console.log('Scale by Value')
ChartObject.data.datasets[0].parsing.yAxisKey='Value'
ChartObject.data.datasets[0].label='Value'
}else{console.log('Scale by Score')
ChartObject.data.datasets[0].parsing.yAxisKey='Score'
ChartObject.data.datasets[0].label='Score'}
ChartObject.update()}
function handleSortOrder(ChartObject,SortByCountry){const original_data=ChartObject.data
if(SortByCountry){const sorted_data=original_data.datasets[0].data.sort((a,b)=>a.CountryCode.localeCompare(b.CountryCode))
ChartObject.data.datasets[0].data=sorted_data
ChartObject.data.labels=sorted_data.map(document=>document.CountryCode)
console.log('Sort by Country')
}else{const sorted_data=original_data.datasets[0].data.sort((a,b)=>a.Value-b.Value)
ChartObject.data.datasets[0].data=sorted_data
ChartObject.data.labels=sorted_data.map(document=>document.CountryCode)
console.log('Sort by Value')}
ChartObject.update()}
const sortOptions=document.getElementById('static-sort-order')
sortOptions.addEventListener('change',()=>{handleSortOrder(StaticChart,sortOptions.checked)})
const scaleOptions=document.getElementById('static-axis-scale')
scaleOptions.addEventListener('change',()=>{handleScaleAxis(StaticChart,scaleOptions.checked)})
class DynamicLineChart{constructor(parentElement,IndicatorCode,CountryList=[]){this.parentElement=parentElement
this.IndicatorCode=IndicatorCode
this.CountryList=CountryList
this.root=document.createElement('div')
this.root.classList.add('chart-section-dynamic-line')
this.parentElement.appendChild(this.root)
this.root.innerHTML=`<div class="chart-section-title-bar"><h2>${IndicatorCode}</h2><button>Random N</button></div>`this.canvas=document.createElement('canvas')
this.context=this.canvas.getContext('2d')
this.root.appendChild(this.canvas)
this.chart=new Chart(this.context,{type:'line',options:{plugins:{legend:{display:false,}},scales:{y:{beginAtZero:true}}}})
this.fetch().then(data=>{this.updateChart(data)})}
async fetch(){const response=await fetch(`/api/v1/dynamic/line/${this.IndicatorCode}`)
try{return response.json()}catch(error){console.error('Error:',error)}}
update(data){this.chart.data=data
this.chart.data.labels=data.labels
this.chart.data.datasets=data.data
this.chart.options.scales=data.scales
this.chart.options.plugins.title=data.title
this.chart.update()}
showRandomN(N=10){let shownIndexArray=Array(N).fill(0).map(()=>Math.floor(Math.random()*this.chart.data.datasets.length))
this.chart.data.datasets.forEach((dataset,index)=>{if(shownIndexArray.includes(index)){dataset.hidden=false}
else{dataset.hidden=true}})
this.chart.options.plugins.legend.display=true
this.chart.update()}}
function setupBarChart(){let Chart=$("#izzy")[0].getContext('2d')
console.log(Chart)
const BarChart=new Chart(BarChartCanvas,{type:'bar',data:{},options:{}})
makeBarChart(BarChart,"BIODIV")}
async function makeBarChart(BarChart,IndicatorCode){let response=await fetch('/api/v1/query/sspi_clean_api_data?IndicatorCode='+IndicatorCode)
let indicator_data=await response.json()
indicator_data.sort((a,b)=>b.RANK-a.RANK)
console.log(indicator_data)
let y_axis=raw?getRaw(indicator_data):getScores(indicator_data)
BarChart.data={labels:getCountries(indicator_data),datasets:[{datacode:IndicatorCode,label:indicator_data[0].IndicatorNameShort,data:y_axis,backgroundColor:'rgb(255, 99, 132)',borderColor:'rgb(255, 99, 132)',borderWidth:1}]}
BarChart.options={elements:{bar:{borderWidth:2,}},scaleShowValues:true,layout:{padding:10},responsive:true,plugins:{legend:{display:false,}},maintainAspectRatio:false,scales:{xAxes:[{id:'x',type:'category',title:{display:true,text:'Country'},ticks:{autoskip:true,}}]}}
BarChart.update();}
function toggleRaw(){raw=!raw
try{IndicatorCode=BarChart.data.datasets[0].datacode
makeBarChart(IndicatorCode);}catch(TypeError){console.log("No Chart Loaded!\n",TypeError)
IndicatorCode=null;}}
function getCountries(indicator_data){return indicator_data.map(data=>data.Country)}
function getScores(indicator_data){return indicator_data.map(data=>data.SCORE)}
function getRaw(indicator_data){return indicator_data.map(data=>data.RAW)}
setupBarChart()
raw=false
async function makeBarChart(BarChart,IndicatorCode){let response=await fetch('/api/v1/query/sspi_clean_api_data?IndicatorCode='+IndicatorCode)
let indicator_data=await response.json()
indicator_data.sort((a,b)=>b.RANK-a.RANK)
console.log(indicator_data)
let y_axis=raw?getRaw(indicator_data):getScores(indicator_data)
BarChart.data={labels:getCountries(indicator_data),datasets:[{datacode:IndicatorCode,label:indicator_data[0].IndicatorNameShort,data:y_axis,backgroundColor:'rgb(255, 99, 132)',borderColor:'rgb(255, 99, 132)',borderWidth:1}]}
BarChart.options={elements:{bar:{borderWidth:2,}},scaleShowValues:true,layout:{padding:10},responsive:true,plugins:{legend:{display:false,}},maintainAspectRatio:false,scales:{xAxes:[{id:'x',type:'category',title:{display:true,text:'Country'},ticks:{autoskip:true,}}]}}
BarChart.update();}
function toggleRaw(){raw=!raw
try{IndicatorCode=BarChart.data.datasets[0].datacode
makeBarChart(IndicatorCode);}catch(TypeError){console.log("No Chart Loaded!\n",TypeError)
IndicatorCode=null;}}
function getCountries(indicator_data){return indicator_data.map(data=>data.Country)}
function getScores(indicator_data){return indicator_data.map(data=>data.SCORE)}
function getRaw(indicator_data){return indicator_data.map(data=>data.RAW)}
var dynamicDataTable=new Tabulator("#methodology-indicator-table",{ajaxURL:"/api/v1/query/metadata/indicator_details",headerSortClickElement:"icon",groupBy:["Pillar","Category"],maxHeight:"100%",groupStartOpen:[true,false],columns:[{title:"Indicator",field:"Indicator",formatter:"textarea",width:200},{title:"Code",field:"IndicatorCodes",width:75},{title:"Policy",field:"Policy",formatter:"textarea",width:200},{title:"Indicator Description",field:"Description",formatter:"textarea",width:400},{title:"Goalposts",field:"GoalpostString"},{title:"Year",field:"SourceYear_sspi_main_data_v3"},]});$(".widget-type-options-menu").hide()
function revealWidgetOptions(){$(".widget-type-options-menu").slideToggle(0.1)}
async function addWidget(widgettype){await $.get(`/widget/${widgettype}`,(data)=>{gsId=crypto.randomUUID()
grid.addWidget({w:6,h:20,minW:4,minH:5,content:data,id:gsId});revealWidgetOptions();}).then(()=>{if(widgettype==="barchart"){setupBarChart(gsId)}});}
function removeWidget(el){widget=$(el).parents('.grid-stack-item')
console.log(widget.attr('gs-id'))
grid.removeWidget(widget.get(0))}
function fullscreenWidget(el){widget=$(el).parents('.grid-stack-item')
console.log(widget.get(0))
console.log(widget.attr('gs-id'))
widgetW=widget.attr('gs-w')
widgetH=widget.attr('gs-h')
console.log(widgetW,widgetH)
fullscreenHeight=Math.floor(0.95*window.innerHeight/25)
grid.update(widget.get(0),{w:12,h:fullscreenHeight})
window.scrollTo(0,widget.offset().top-10)
fullscreenButton=widget.find(".fullscreen-button").attr("onclick",`returnWidgetToOriginalSize(this,${widgetW},${widgetH})`)}
function returnWidgetToOriginalSize(el,widgetW,widgetH){$(el).parents().eq(2).attr('gs-id')
widget=$(`[gs-id=${widgetId}]`).get(0)
grid.update(widget,{w:widgetW,h:widgetH})
fullscreenButton=$(`[gs-id=${widgetId}]`).find(".fullscreen-button").attr("onclick","fullscreenWidget(this)")}
function setupBarChart(gsId){let BarChartCanvas=$(`[gs-id=${gsId}]`).find(".bar-chart").get(0)
console.log(BarChartCanvas)
const BarChart=new Chart(BarChartCanvas,{type:'bar',data:{},options:{}})
makeBarChart(BarChart,"BIODIV")}