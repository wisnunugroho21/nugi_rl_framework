import numpy as np

from eps_runner.standard import StandardRunner

class SlimeVolleyRunner(StandardRunner):
    def run_discrete_iteration(self, agent = None):
        if agent is None:
            agent = self.agent

        for _ in range(self.n_update):
            action = agent.act(self.states)

            if action == 0:
                action_gym = [0, 0, 0] # NOOP
            elif action == 1:
                action_gym = [1, 0, 0] # LEFT (forward)
            elif action == 2:
                action_gym = [0, 1, 0] # RIGHT (backward)
            elif action == 3:
                action_gym = [0, 0, 1] # UP (jump)
            elif action == 4:
                action_gym = [1, 0, 1] # UPLEFT (forward jump)
            elif action == 5:
                action_gym = [0, 1, 1] # UPRIGHT (backward jump)

            next_state, reward, done, _ =  self.env.step(action_gym)     
            
            if self.training_mode:
                agent.save_eps(self.states.tolist(), action, reward, float(done), next_state.tolist())
                
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
        
        return agent