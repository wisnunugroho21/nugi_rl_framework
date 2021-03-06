import torch

from distribution.categorical_distribution import sample
from ppo_loss.truly_ppo_discrete_impala import get_loss
from ppo_agent.agent_impala import AgentImpala
from utils.pytorch_utils import set_device, to_numpy

class AgentDiscrete(AgentImpala):  
    def __init__(self, Actor_Model, Critic_Model, state_dim, action_dim, 
                is_training_mode = True, policy_kl_range = 0.0008, policy_params = 20, value_clip = 1.0, 
                entropy_coef = 0.0, vf_loss_coef = 1.0, minibatch = 4, PPO_epochs = 4, 
                gamma = 0.99, lam = 0.95, learning_rate = 2.5e-4, folder = 'model', use_gpu = True):
                        
        super(AgentDiscrete, self).__init__(Actor_Model, Critic_Model, state_dim, action_dim, 
                is_training_mode, policy_kl_range, policy_params, value_clip, 
                entropy_coef, vf_loss_coef, minibatch, PPO_epochs, 
                gamma, lam, learning_rate, folder, use_gpu)

    def act(self, state):
        state         = torch.FloatTensor(state).unsqueeze(0).to(self.device).detach()
        action_probs  = self.actor(state)
        
        # We don't need sample the action in Test Mode
        # only sampling the action in Training Mode in order to exploring the actions
        if self.is_training_mode:
            # Sample the action
            action = sample(action_probs)            
        else:            
            action = torch.argmax(action_probs, 1)  
              
        return action, to_numpy(action_probs.squeeze(0), self.use_gpu)

    # Get loss and Do backpropagation
    def training_ppo(self, states, actions, rewards, dones, next_states, worker_action_probs): 
        action_probs, values          = self.actor(states), self.critic(states)
        old_action_probs, old_values  = self.actor_old(states), self.critic_old(states)
        next_values                   = self.critic(next_states)

        loss = get_loss(action_probs, worker_action_probs, old_action_probs, values, old_values, next_values, actions, rewards, dones,
                self.policy_kl_range, self.policy_params, self.value_clip, self.vf_loss_coef, self.entropy_coef, self.use_gpu)                

        self.actor_optimizer.zero_grad()
        self.critic_optimizer.zero_grad()

        loss.backward()            

        self.actor_optimizer.step() 
        self.critic_optimizer.step()