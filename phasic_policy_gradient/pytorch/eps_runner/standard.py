import numpy as np

from eps_runner.runner import Runner
from memory.list_memory import ListMemory

class StandardRunner(Runner):
    def __init__(self, env, render, training_mode, n_update, agent = None, max_action = 1, writer = None, n_plot_batch = 1):
        self.env                = env
        self.agent              = agent
        self.render             = render
        self.training_mode      = training_mode
        self.n_update           = n_update
        self.max_action         = max_action
        self.writer             = writer
        self.n_plot_batch       = n_plot_batch

        self.t_updates          = 0
        self.t_aux_updates      = 0
        self.i_episode          = 0
        self.total_reward       = 0
        self.eps_time           = 0

        self.states             = self.env.reset()
        self.memories           = ListMemory()

    def run_discrete_iteration(self, agent):
        self.memories.clear_memory()

        for _ in range(self.n_update):
            action = int(agent.act(self.states))
            next_state, reward, done, _ = self.env.step(action)
            
            if self.training_mode:
                self.memories.save_eps(self.states.tolist(), action, reward, float(done), next_state.tolist())
                
            self.states         = next_state
            self.eps_time       += 1 
            self.total_reward   += reward
                    
            if self.render:
                self.env.render()

            if done:                
                self.i_episode  += 1
                print('Episode {} \t t_reward: {} \t time: {} '.format(self.i_episode, self.total_reward, self.eps_time))

                if self.i_episode % self.n_plot_batch == 0 and self.writer is not None:
                    self.writer.add_scalar('Rewards', self.total_reward, self.i_episode)
                    self.writer.add_scalar('Times', self.eps_time, self.i_episode)

                self.states         = self.env.reset()
                self.total_reward   = 0
                self.eps_time       = 0             
        
        return self.memories

    def run_continous_iteration(self, agent = None):
        self.memories.clear_memory()       

        eps_rewards = []
        for _ in range(self.n_update):
            action = agent.act(self.states) 

            action_gym = np.clip(action, -1.0, 1.0) * self.max_action
            next_state, reward, done, _ = self.env.step(action_gym)
            
            if self.training_mode:
                self.memories.save_eps(self.states.tolist(), action, reward, float(done), next_state.tolist())
                
            self.states         = next_state
            self.eps_time       += 1 
            self.total_reward   += reward
                    
            if self.render:
                self.env.render()

            if done:                
                self.i_episode  += 1
                eps_rewards.append(self.total_reward)

                print('Episode {} \t t_reward: {} \t time: {} '.format(self.i_episode, self.total_reward, self.eps_time))

                if self.i_episode % self.n_plot_batch == 0 and self.writer is not None:
                    self.writer.add_scalar('Rewards', self.total_reward, self.i_episode)
                    self.writer.add_scalar('Times', self.eps_time, self.i_episode)

                self.states         = self.env.reset()
                self.total_reward   = 0
                self.eps_time       = 0        

        return self.memories