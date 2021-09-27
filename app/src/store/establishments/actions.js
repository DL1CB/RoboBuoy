import { db } from '../digireglocalbase'

export function fetchEstablishments ( { commit } ) {
    db.collection('establishments').orderBy('timestamp','desc').get().then(establishments => {
        commit('updateEstablishments',establishments)
    })
}

export function clearEstablishments ( { commit } ) {
    db.collection('establishments').delete()
    commit('clearEstablishments')      
}

export function addEstablishment ( { commit }, establishment) {
    establishment.timestamp = (new Date()).getTime()
    console.log('addEstablishment', establishment)
    db.collection('establishments').add(establishment).then( ()=>{

        db.collection('establishments').orderBy('timestamp','desc').get().then(establishments => {
            commit('updateEstablishments',establishments)
        })

    })
}

export function removeEstablishment ( { commit }, establishment) {
    db.collection('establishments').doc({timestamp:establishment.timestamp}).delete().then(()=>{

        db.collection('establishments').orderBy('timestamp','desc').get().then(establishments => {
            commit('updateEstablishments',establishments)
        })
        
    })
}


