<template>
  <div class="q-pa-lg">

    <q-card v-if="step==1"  class="my-card">
      <q-card-section >
        <q-input outlined label="Full Name" v-model="name"  />
        <q-input outlined label="Telephone Number" v-model="phone"/>
        <q-input outlined label="Email" v-model="email" />
      </q-card-section>
              <q-card-actions vertical>
        <q-btn
        @click="connectDigireg"
        class="glossy"
        rounded
        color="primary"
        label="Register Blue"
        />
        </q-card-actions>
    </q-card>

    <q-card v-if="step==2" class="my-card">
      <q-card-section>
        <q-img src="/bluetooth.svg" basic></q-img>
      </q-card-section>
    </q-card>

    <q-card v-if="step==3" class="my-card">
      <q-card-section>
        <q-img src="/encrypt.svg" basic></q-img>
      </q-card-section>
    </q-card>

    <q-card v-if="step==4" class="my-card">
      <q-card-section>
        <q-img src="/transfer.svg" basic></q-img>
      </q-card-section>
    </q-card>


    <q-card v-if="step==5" class="my-card">
      <q-card-section>
        <q-img src="/success.svg" basic></q-img>
      </q-card-section>
    </q-card>

    <q-card v-if="establishments.length" flat bordered class="my-card">
        <q-card-section>

            <q-timeline color="secondary">
                <q-timeline-entry
                    v-for="item in establishments"
                    :key="item.timestamp"
                    :title="item.name">
                    {{ item.street }} {{ item.city }} {{ item.zip }}<br />
                    {{ item.state }} {{ item.country }}<br />
                    {{ item.phone }} <br />
                    {{ item.email }} <br />
                    {{ item.id }} <br />

                    <div slot="subtitle" class="row">
                      <div class="col-10 ">
                          {{formatDate(new Date(item.timestamp), 'D MMM YYYY - h:mm a')}}
                      </div>
                      <div class="col-2" @click="removeEstablishment(item)">
                          <q-icon size="md" name="delete" />
                      </div>
                    </div>

                </q-timeline-entry>
            </q-timeline>
        </q-card-section>
    </q-card>

    <!--q-card>
        <div v-for="(item, index) in logs" :key="index">
            {{item}}
        </div>
    </q-card-->

  </div>
</template>

<script>

import { date } from "quasar"
import { createNamespacedHelpers } from "vuex"

import encode from '../networking/encode'
import { decodeTransformer } from '../networking/decode'

const establishments = createNamespacedHelpers("establishments")

export default {

    name: "DigiReg",

    mounted: function () {
        this.fetchEstablishments()
    },

    data() {
        return {
            step:1,
            date: (new Date()).getTime(),
            name:"",
            phone:"",
            email:"",
            logs:[]
        }
    },

    computed: {
        ...establishments.mapState(["establishments"])
    },

    methods: {

        log( args ){
            console.log(args)
            this.logs.push( args )
        },

        ...establishments.mapActions(["fetchEstablishments", "addEstablishment", "removeEstablishment"]),

        formatDate: date.formatDate,

        async connectDigireg(){

            const log = this.log

            try {
                
                const serviceUuid = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
                const RXcharacteristicUuid = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
                const TXcharacteristicUuid = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

                this.step=2

                const device = await navigator.bluetooth.requestDevice({ filters: [{ services: [serviceUuid] }] })

                this.step=3

                const server = await device.gatt.connect()

                const service = await server.getPrimaryService(serviceUuid)

                const txcharacteristic = await service.getCharacteristic(TXcharacteristicUuid)

                var decoder = decodeTransformer( (data) => {
                  console.log( data )
                  this.addEstablishment(data)
                })

                let utf8decoder = new TextDecoder()

                await txcharacteristic.startNotifications()

                await txcharacteristic.addEventListener(
                    "characteristicvaluechanged",
                    function( event ){
                        console.log( event )
                        decoder( utf8decoder.decode(event.target.value ) , "utf-8")
                    }
                )

                const rxcharacteristic = await service.getCharacteristic(RXcharacteristicUuid)

                this.step=4
       
                const str = encode({ date:this.date, name:this.name, phone:this.phone, email:this.email })

                for (  var i=0; i <= str.byteLength; i=i+20){
                  await rxcharacteristic.writeValue( str.slice(i,i+20) )
                  await new Promise(r => setTimeout(r, 100))
                }
               
                await new Promise(r => setTimeout(r, 1000)) //sleep

                await txcharacteristic.stopNotifications()

                this.step=5

                const disconnectresult = await device.gatt.disconnect()

                await new Promise(r => setTimeout(r, 1000)) //sleep
                this.step=1
    
            } catch (error) {           
                log(error)
                this.step=1
            }
        }
    }
}
</script>