import os
import torch
import argparse
import numpy as np

from pybullet_envs import *
from algorithm.sac import SAC
from algorithm.metalearner import MetaLearner
from configs import cheetah_dir, cheetah_vel

p = argparse.ArgumentParser()
p.add_argument(
    '--env', type=str, default='dir',
    help='Env to use: default cheetah-dir'
)
p.add_argument(
    '--gpu_index', type=int, default=0,
    help='Set a GPU index')
args = p.parse_args()


def trainer():
    if args.env == 'dir':
        config = cheetah_dir.config
    elif args.env == 'vel':
        config = cheetah_vel.config
    else:
        NotImplementedError

    # Create a multi-task environment and sample tasks
    env = envs[config['env_name']](**config['env_params'])
    tasks = env.get_all_task_idx()

    observ_dim = env.observation_space.shape[0]
    action_dim = env.action_space.shape[0]
    latent_dim = config['latent_size']
    hidden_units = list(map(int, config['hidden_units'].split(",")))
    encoder_input_dim = observ_dim + action_dim + 1
    encoder_output_dim = latent_dim * 2

    agent = SAC(
        observ_dim=observ_dim,
        action_dim=action_dim,
        latent_dim=latent_dim,
        hidden_units=hidden_units,
        encoder_input_dim=encoder_input_dim,
        encoder_output_dim=encoder_output_dim,
        device=torch.device('cuda', index=args.gpu_index) if torch.cuda.is_available() else torch.device('cpu'),
        **config['sac_params'],
    )

    meta_learner = MetaLearner(
        env=env,
        agent=agent,
        train_tasks=list(tasks[:config['n_train_tasks']]),
        eval_tasks=list(tasks[-config['n_eval_tasks']:]),
        **config['pearl_params']
    )

    # Run meta-training
    # train_results = meta_learner.meta_train()

    # Run meta-testing
    # test_results = meta_learner.meta_test()

if __name__ == "__main__":
    trainer()

