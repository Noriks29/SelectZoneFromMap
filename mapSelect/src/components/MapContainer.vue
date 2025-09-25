<template>
    <div class="MainPage">
        <div>
        <Toolbar class="mb-4">
            <template #start>
                <FileUpload mode="basic" name="file" accept=".txt,text/plain" :maxFileSize="100000000" :customUpload="true" @select="LoadFile" :auto="true" :chooseLabel="'Загрузить'" />
                <Button icon="pi pi-download" label="Скачать" style="margin-left: 5px;" @click="downloadTextFile"/>
            </template>
            <template #end>
                <Button icon="pi pi-refresh" severity="warning" text rounded style="margin-left: 5px;" @click="ReloadMapContainer"/>
            </template>
        </Toolbar>
        <DataTable :value="safeData" scrollable scrollHeight="95vh"
        tableStyle="min-width: 30rem">
        <Column field="name" header="Название" sortable headerStyle="width: 10rem">
            <template #body="slotProps">
                <InputText type="text" v-model="slotProps.data.name" style="width: 10rem;"/>
            </template>
        </Column>
        <Column field="x.p1" header="Широта" sortable>
            <template #body="slotProps">
                <p>1: {{slotProps.data.x.p1.toFixed(3)}}</p>
                <p>2: {{slotProps.data.x.p2?.toFixed(3)}}</p>
            </template>
        </Column>
        <Column field="y.p1" header="Долгота" sortable>
            <template #body="slotProps">
                <p>: {{ slotProps.data.y.p1.toFixed(3)}}</p>
                <p>: {{ slotProps.data.y.p2?.toFixed(3)}}</p>
            </template>
        </Column>
        <Column header=""  headerStyle="width: 3rem">
            <template #body="slotProps">
                <Button icon="pi pi-trash"  @click="DeleteRow(slotProps.data)" severity="danger" text rounded/>
            </template>
        </Column>
        </DataTable>
    </div>
    <div class="MapContain">
        <div id="map"></div>
    </div>
  </div>
</template>


<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import icon from 'leaflet/dist/images/marker-icon.png';
import icon2x from 'leaflet/dist/images/marker-icon-2x.png';
import shadow from 'leaflet/dist/images/marker-shadow.png';


import Button from 'primevue/button';
import Toolbar from 'primevue/toolbar';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InputText from 'primevue/inputtext';
import FileUpload from 'primevue/fileupload';

import download from 'downloadjs';

export default {
  name: 'MapContain',
  data(){
      return{
        map: {},
        safeData: [],
        newRow: true,
        index: 0,
    }
  },
  components:{
    Button, Toolbar, DataTable, Column, InputText, FileUpload
  },
  methods: {
        async LoadFile(event){
            const file = event.files[0]; // Получаем первый файл
            if (!file) {
                console.error('Файл не выбран');
                return;
            }
            try {
                const reader = new FileReader();
                reader.readAsText(file);
                reader.onload = (event) => {
                    this.newRow = true
                    let data = event.target.result.split("\n")
                    data.forEach(element => {
                        let rec = element.split(" ")
                        let x1 = Number(rec[1]);let x2 = Number(rec[3]);let y1 = Number(rec[2]);let y2 = Number(rec[4])
                        let newRow = {index: this.index, name: rec[0], x:{p1:x1, p2:x2}, y:{p1:y1, p2:y2}, p1: this.DrowCircle(x1,y1), p2:this.DrowCircle(x1,y1), rec: undefined}
                        this.DrowRectangle(newRow)
                        this.safeData.push(newRow)
                        this.index++
                    });
                }; 
                reader.onerror = (error) => {
                    reject(error);
                };
            } catch (error) {
                console.error('Ошибка чтения файла:', error);
            }
        },
        downloadTextFile() {
            const text = this.safeData.map(item => 
                item.name+" "+item.x.p1+" "+item.y.p1+" "+item.x.p2+" "+item.y.p2
            ).join('\n');
            console.log(text)
            download(text, "ZoneData_" + new Date().toISOString().slice(0, 10)+".txt" ,'text/plain')
        },
      async CreateMap(){
          this.map = L.map('map', {zoomAnimation: true}).setView(new L.LatLng(55, 60), 3);
          L.tileLayer('http://localhost:8080/map/{z}/{x}/{y}.png', 
          {
            minZoom: 1, 
            maxZoom: 6,
            attribution: ''
          }).addTo(this.map);
          let DefaultIcon = new L.icon({
                iconUrl: icon,
                shadowUrl: shadow,
                iconRetinaUrl: icon2x
          });
          L.Marker.prototype.options.icon = DefaultIcon;
          this.map.on('click', (e) => {
              const { lat, lng } = e.latlng;
              this.AddRow(lat,lng)
              console.log(`Широта: ${lat}, Долгота: ${lng}`);
          });
        },
        async ReloadMapContainer(){
          this.map.off();
          this.map.remove();
          this.CreateMap()
        },
        AddRow(x,y){
            if(this.newRow){
                let point = this.DrowCircle(x,y)
                this.safeData.push({index: this.index, name: this.index, x:{p1: x, p2:null}, y:{p1: y, p2: null}, p1: point, p2:undefined, rec: undefined})
                this.newRow = false
                this.index++
            }
            else{
                let point = this.DrowCircle(x,y)
                const data = this.safeData[this.safeData.length - 1]
                data.x.p2 = x
                data.y.p2 = y
                data.p2 = point
                this.newRow = true
                this.DrowRectangle(data)
            }
        },
        DrowCircle(x,y){
            return L.circle([x,y], 2000, {
                color: 'red',
                fillColor: '#f03',
                fillOpacity: 0.4
            }).addTo(this.map)
        },
        DrowRectangle(data){
            data.rec = L.rectangle([[data.x.p1,data.y.p1],[data.x.p2,data.y.p2]], {color: "#ff7800", weight: 1}).addTo(this.map);
        },
        DeleteRow(data){
            for (let i = 0; i < this.safeData.length; i++) {
                const element = this.safeData[i];
                if(element.index == data.index){
                    this.map.removeLayer(element.p1)
                    if(element.p2 != undefined) this.map.removeLayer(element.p2)
                    if(element.rec != undefined) this.map.removeLayer(element.rec)
                    if(!this.newRow && i == this.safeData.length-1) this.newRow = true
                    this.safeData.splice(i, 1)
                }
            }
        }
    },
    async mounted() {
      this.CreateMap()
    }
}
</script>


<style lang="scss">
#map{
    height: 100vh;
}
.MapContain{
    flex: 1;
}
.MainPage{
  display: flex;
}
</style>
