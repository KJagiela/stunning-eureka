<template>
  <Transition name="modal">
    <div v-if="show" class="modal-mask">
      <div class="modal-wrapper">
        <div class="modal-container">
          <div class="modal-header">
            <slot name="header"></slot>
          </div>

          <div class="modal-footer">
            <slot name="footer">
              <button
                class="modal-default-button  red-button"
                @click="$emit('no')">
                No
              </button>
              <button
                class="modal-default-button"
                @click="$emit('yes')">
                Yes
              </button>
            </slot>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>
<script>
export default {
  name: 'ConfirmationModal',
  props: {
    show: Boolean
  }
}
</script>

<style>
.modal-mask {
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: table;
  transition: opacity 0.3s ease;
}

.modal-wrapper {
  display: table-cell;
  vertical-align: middle;
}

.modal-container {
  width: 300px;
  margin: 0px auto;
  padding: 20px 30px;
  background-color: #2c3e50;
  border-radius: 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.33);
  transition: all 0.3s ease;
}

.modal-header h3 {
  margin-top: 0;
  color: #42b983;
  text-align: center;
}

.modal-footer {
  display: flex;
  justify-content: space-evenly;
}

.modal-default-button {
   padding: 8px 32px;
   box-shadow: 0px 0px 12px -2px rgba(0,0,0,0.5);
   line-height: 1.25;
   background: #214f2b;
   text-decoration: none;
   color: white;
   font-size: 16px;
   text-transform: uppercase;
   position: relative;
   overflow: hidden;
}

.red-button {
  background: #4b1818;
}

.modal-enter-from {
  opacity: 0;
}

.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  -webkit-transform: scale(1.1);
  transform: scale(1.1);
}
</style>
