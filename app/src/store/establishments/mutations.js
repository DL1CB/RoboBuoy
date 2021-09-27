export function addEstablishment ( state, establishment ) {
    state.establishments.push(establishment)
}

export function updateEstablishments ( state, establishments ) {
    state.establishments = establishments
}

export function clearEstablishments ( state ) {
    state.establishments = []
}