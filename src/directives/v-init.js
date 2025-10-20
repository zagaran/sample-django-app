import Vue from "vue";

function set(context, path, value) {
    /**
     * set is a helper function which allows us to dynamically target and set values within an object, allowing
     * v-init to interpret a model like 'listPullParams.housing_type' as context['listPullParams']['housing_type']
     */
    var pList = path.split('.')
    if (pList.length > 2) { throw "You cannot use v-init with a nest factor of > 2 e.g. a.b.c" }
    if (pList.length >= 2) {
        // we are setting the value of pList[0][pList[1]] = value
        var target = pList.shift();
        if (context.$data[target] === undefined) {
            context.$data[target] = {}
        }
        set(context[target], pList.join('.'), value);
    }
    else {
       context[pList[0]] = value
    }
}

const initArgToModel = (arg) => {
    // Convert v-init arg to v-model format
    const fieldKeys = arg.split(':').map((key) => {
        // convert each field key from kebab-case to camelCase
        const camelChunks = key.split('-').map((chunk, i) => {
            if (i === 0) { return chunk } //
            return chunk.charAt(0).toUpperCase() + chunk.substring(1)
        })
        return camelChunks.join("")
    })
    return fieldKeys.join('.')
}


const VInit = [
    // v-init automatically sets the data value on page load; the expression is given by the binding argument
    'init',
    {
        beforeMount(el, binding, vNode) {
            if (!binding.arg) {
              console.log(el, binding, vNode)
              throw new Error("You cannot use v-init without providing an argument.")
            }
            const expression = initArgToModel(binding.arg)
            set(binding.instance, expression, binding.value);
            binding.instance.$nextTick(() => {binding.instance.$forceUpdate()});
        }
    }
]

export default VInit;
