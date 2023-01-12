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
        v-if="jobs"
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
      <ConfirmationModal :show="showBlacklistModal" @yes="blacklistCompany" @no="showBlacklistModal=false;currentJobId+=1">
        <template v-slot:header>
          <h3>Blacklist the company as well?</h3>
        </template>
      </ConfirmationModal>
      <ConfirmationModal :show="showHypeModal" @yes="markJobHyped" @no="markJobInterested">
        <template v-slot:header>
          <h3>Are you hyped tho?</h3>
        </template>
      </ConfirmationModal>
    </div>
</template>
<script>
import axios from 'axios'
import ConfirmationModal from "./ConfirmationModal.vue";
export default {
  name: "SwipableCard",
  components: {ConfirmationModal},
  data() {
    return {
      startX: null,
      jobs: null,
      currentJobId: 0,
      showBlacklistModal: false,
      showHypeModal:false,
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
    this.grabJobs()
  },
  mounted() {
    document.addEventListener('keyup', this.handleKey)
  },
  methods: {
    grabJobs() {
      axios
        .get('http://localhost:8008/api/grabbo/jobs/')
        .then((response) => {
          this.jobs = response.data.results;
        })
    },
    handleKey (e) {
      if (e.key === 'ArrowRight') this.showHypeModal = true
      if (e.key === 'ArrowLeft') this.blacklistJob()
    },
    dragMe(evt, item) {
      evt.dataTransfer.dropEffect = 'move'
      evt.dataTransfer.effectAllowed = 'move'
      this.startX = evt.clientX
    },
    abortMe(evt) {
      if(evt.clientX > this.startX + 50) {
        this.showHypeModal = true
      }
      if(evt.clientX < this.startX - 50) {
        this.blacklistJob()
      }
    },
    markJobInterested() {
      axios
        .post(
          `http://localhost:8008/api/grabbo/job/${this.current.id}/`,
          {hype: 2},
        )
        this.showHypeModal = false;
      this.currentJobId += 1;
    },
    markJobHyped() {
      axios
        .post(
          `http://localhost:8008/api/grabbo/job/${this.current.id}/`,
          {hype: 3},
        )
        this.showHypeModal = false;
      this.currentJobId += 1;
    },
    blacklistJob() {
      axios.post(
          `http://localhost:8008/api/grabbo/job/${this.current.id}/`,
          {hype: 1},
      )
      this.showBlacklistModal = true;
    },
    blacklistCompany() {
      axios.post(
          `http://localhost:8008/api/grabbo/company/${this.current.company_id}/`,
          {hype: 1},

      )
      this.showBlacklistModal = false;
      this.grabJobs()
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
