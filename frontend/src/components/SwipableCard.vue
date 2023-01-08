<template>
    <div
      class="draggable-container" @drop="abortMe"
      @dragover.prevent
      @dragenter.prevent
      @keyup.right="markInterested"
      @keyup.left="markBlacklisted"
    >
      <div
        class="draggable-card"
        draggable="true"
        @dragstart="dragMe"
      >
        <div class="job-description">
          <h2 class="job-name">{{ this.current.title }}</h2>
          <h3 class="company-name">{{ this.current.company_name }} (Size: {{ this.current.company_size }})</h3>
          <div class="salary">Salary: {{ this.current.salary}}</div>
          <div class="job-category"> Cat: {{ this.current.category }}, tech: {{ this.current.technology }}</div>
          <div>{{ this.current.description}}</div>
          <a :href="this.current.url" target="_blank">See it</a>
        </div>
      </div>
    </div>
</template>
<script>
import axios from 'axios'
export default {
  name: "SwipableCard",
  data() {
    return {
      startX: null,
      jobs: null,
      currentJobId: 0,
    }
  },
  computed: {
    current() {
      if (!!this.jobs){
        return this.jobs[this.currentJobId];
      }
    },
  },
  created() {
    axios
        .get('http://localhost:8008/api/grabbo/jobs/')
        .then((response) => {
          this.jobs = response.data.results;
        })
  },
  mounted() {
    document.addEventListener('keyup', this.handleKey)
  },
  methods: {
    handleKey (e) {
      if (e.key === 'ArrowRight') this.markInterested()
      if (e.key === 'ArrowLeft') this.markBlacklisted()
    },
    dragMe(evt, item) {
      evt.dataTransfer.dropEffect = 'move'
      evt.dataTransfer.effectAllowed = 'move'
      this.startX = evt.clientX

    },
    abortMe(evt) {
      if(evt.clientX > this.startX + 50) {
        this.markInterested()
      }
      if(evt.clientX < this.startX - 50) {
        this.markBlacklisted()
      }
    },
    markInterested() {
      axios.post(
          `http://localhost:8008/api/grabbo/jobs/${this.current.id}/`,
          {hype: 2},
      )
    },
    markBlacklisted() {
      axios.post(
          `http://localhost:8008/api/grabbo/jobs/${this.current.id}/`,
          {hype: 1},
      )
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
  font-size: 1.5em;
  color: #993333;
}

a {
  color: #4b1818;
}
</style>
