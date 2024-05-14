# authors
Description: List of authors
Created on Tue May 14 01:05:23 2024

Found 2 results from 2024-05-07 to 2024-05-14
OpenAlex URLS (not including from_created_date or the API key)
- [https://api.openalex.org/works?filter=author.id%3Ahttps%3A//openalex.org/A5003442464](https://api.openalex.org/works?filter=author.id%3Ahttps%3A//openalex.org/A5003442464)

## CatTSunami: Accelerating Transition State Energy Calculations with
  Pre-trained Graph Neural Networks   

OpenAlex: https://openalex.org/W4396781988    
Open access: True
    
[Brook Wander](https://openalex.org/A5029824000), [Muhammed Shuaibi](https://openalex.org/A5004640526), [John R. Kitchin](https://openalex.org/A5003442464), [Zachary W. Ulissi](https://openalex.org/A5024574386), [C. Lawrence Zitnick](https://openalex.org/A5058450549), arXiv (Cornell University). None(None)] 2024.https://doi.org/10.48550/arxiv.2405.02078 ([pdf](https://arxiv.org/pdf/2405.02078)).
    
Direct access to transition state energies at low computational cost unlocks the possibility of accelerating catalyst discovery. We show that the top performing graph neural network potential trained on the OC20 dataset, a related but different task, is able to find transition states energetically similar (within 0.1 eV) to density functional theory (DFT) 91% of the time with a 28x speedup. This speaks to the generalizability of the models, having never been explicitly trained on reactions, the machine learned potential approximates the potential energy surface well enough to be performant for this auxiliary task. We introduce the Open Catalyst 2020 Nudged Elastic Band (OC20NEB) dataset, which is made of 932 DFT nudged elastic band calculations, to benchmark machine learned model performance on transition state energies. To demonstrate the efficacy of this approach, we replicated a well-known, large reaction network with 61 intermediates and 174 dissociation reactions at DFT resolution (40 meV). In this case of dense NEB enumeration, we realize even more computational cost savings and used just 12 GPU days of compute, where DFT would have taken 52 GPU years, a 1500x speedup. Similar searches for complete reaction networks could become routine using the approach presented here. Finally, we replicated an ammonia synthesis activity volcano and systematically found lower energy configurations of the transition states and intermediates on six stepped unary surfaces. This scalable approach offers a more complete treatment of configurational space to improve and accelerate catalyst discovery.    

    

## AdsorbDiff: Adsorbate Placement via Conditional Denoising Diffusion   

OpenAlex: https://openalex.org/W4396813915    
Open access: True
    
[Adeesh Kolluru](https://openalex.org/A5017163658), [John R. Kitchin](https://openalex.org/A5003442464), arXiv (Cornell University). None(None)] 2024.https://doi.org/10.48550/arxiv.2405.03962 ([pdf](https://arxiv.org/pdf/2405.03962)).
    
Determining the optimal configuration of adsorbates on a slab (adslab) is pivotal in the exploration of novel catalysts across diverse applications. Traditionally, the quest for the lowest energy adslab configuration involves placing the adsorbate onto the slab followed by an optimization process. Prior methodologies have relied on heuristics, problem-specific intuitions, or brute-force approaches to guide adsorbate placement. In this work, we propose a novel framework for adsorbate placement using denoising diffusion. The model is designed to predict the optimal adsorbate site and orientation corresponding to the lowest energy configuration. Further, we have an end-to-end evaluation framework where diffusion-predicted adslab configuration is optimized with a pretrained machine learning force field and finally evaluated with Density Functional Theory (DFT). Our findings demonstrate an acceleration of up to 5x or 3.5x improvement in accuracy compared to the previous best approach. Given the novelty of this framework and application, we provide insights into the impact of pre-training, model architectures, and conduct extensive experiments to underscore the significance of this approach.    

    
