function D = dsi_subj(data_dir, S, sn,brain_side,sess_nm,dcst, icst, rst,varargin)
% function to extract qa from eact txt file  - b:brain_side

%tract_dir = fullfile(data_dir, 'no_correction');

Brain_side = {'L','R'};
Tract_types = {'DCST','ICST','RST'};

if nargin<3
    if S.brain_side == 12
        b = (1:2);
    else 
        b = S.brain_side;
    end 
else
    b = brain_side;
end

D = [];
%loop through session & tract types
for i = b
    for b = sess_nm
        if nargin <4 %use all tracts
            tract_nm = [1:3]
        end 
        for t = tract_nm
            if nargin < 4
                tract_files = dir(fullfile(tract_dir,[S.Subj_id{i} '_' S.Sess_id{i} '_' Tract_types{t} '_' Brain_side{b} '.txt']));
            end
        end
    end
end
end

                

        
