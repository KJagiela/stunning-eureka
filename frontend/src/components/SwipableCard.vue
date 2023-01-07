<template>
    <div
      class="draggable-container" @drop="abortMe"
      @dragover.prevent
      @dragenter.prevent
    >
      <div
        class="draggable-card"
        draggable="true"
        @dragstart="dragMe"
      >
        <div class="job-description">{{ this.current }}</div>
      </div>
      <div
        class="dummy-card"
      >
        <div class="job-description">{{ this.next }}</div>
      </div>
    </div>
</template>
<script>
export default {
  name: "SwipableCard",
  data() {
    return {
      startX: null,
      jobs: ['job1', 'job2', 'job3'],
      currentJobId: 0,
    }
  },
  computed: {
    current() {
      return this.jobs[this.currentJobId];
    },
    next() {
      return this.jobs[this.currentJobId + 1];
    }
  },
  methods: {
    dragMe(evt, item) {
      // evt.dataTransfer.dropEffect = 'move'
      // evt.dataTransfer.effectAllowed = 'move'
      // evt.dataTransfer.setData('itemID', item.id)
      this.startX = evt.clientX
    },
    abortMe(evt) {
      console.log(this.startX)
      if(evt.clientX > this.startX + 50) {
        console.log('Fajne')
      }
      if(evt.clientX < this.startX - 50) {
        console.log('Niefajne')
      }
    }
  }
}
</script>

<style scoped>

.draggable-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.draggable-card {
  position: absolute;
  background-color: #2aabd2;
  border-radius: 10px;
  height: 500px;
  width: 400px;
  text-align: center;
  z-index: 2;
}
.job-description {
  position: relative;
  top: 50%;
  font-size: 1.5em;
  color: #993333;
}
.dummy-card {
  position: absolute;
  z-index: 1;
  background-color: #2b669a;
  border-radius: 10px;
  height: 500px;
  width: 400px;
}
</style>
