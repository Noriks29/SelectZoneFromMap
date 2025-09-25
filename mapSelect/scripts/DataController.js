import {ref} from "vue";

const GlobalDataPlugin = {
  install(app) {

    const apiVite = app.config.globalProperties
    

    // работа с наземными пунктами 
    const ZoneList = ref([]);
    const $ZoneList = function () {
        return ZoneList
    };
    const $ZoneListAdd = function (x,y) {
        console.log(ZoneList.value.length, ZoneList.value)
    };
    apiVite.$ZoneList = $ZoneList
    apiVite.$ZoneListAdd = $ZoneListAdd

  },
};

export default GlobalDataPlugin;