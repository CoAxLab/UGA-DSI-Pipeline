function varargout = dsi_analysis(what, varargin)
    % Define the base directory where the files are located
    base_dir = 'D:\DSI\DSI_Pilot';
    data_dir = fullfile(base_dir, 'data','qa');
    analysis_dir = fullfile(base_dir, 'analysis');

    % Define the subject Subject_IDs and pairs of files to be processed
    subject_file = 'subj_list.txt';
    S = mydload(fullfile(data_dir, subject_file));
    nsess = length(S.sn);

switch (what)
    case 'subject_list'
        if nargin < 2
                sn = (1:nsess);
        else
                sn = varargin{1};
        end

        fprintf('\nsn\t Subj_id\t subj_nm\t Group\t Sess_id\t sess_nm\t brain_side\t lesion\t dcst\t icst\t rst\t Tract_type\n');
        fprintf('n--\t-------\t------\t-----\t-------\t-------\t----------\t------\t----\t----\t---\t----------\n');

        for s = sn 
        % Printing subject list
            fprintf([num2str(S.sn(s)) '\t' S.Subj_id{s} '\t' num2str(S.subj_nm(s)) '\t' S.Group{s} '\t\t'...
                    S.Sess_id{s} '\t' num2str(S.sess_nm(s)) '\t' num2str(S.brain_side(s)) '\t\t'... 
                    num2str(S.lesion(s)) '\t' num2str(S.dcst(s)) '\t' num2str(S.icst(s)) '\t\t'...
                    num2str(S.rst(s)) '\t' S.Tract_type{s} '\n']);
        end 
        fprintf('\n');
        varargout = {S};

    case 'preprocess_QA'
        D = struct();
        if nargin < 2
            sn = (1:nsess);
        else 
            sn = varargin{1};
        end 
        for i = sn
            disp(['Extracting QA for subject: ' S.Subj_id{i} '_' S.Sess_id{i} '_' S.Tract_type{i} '.txt']);
            % Load .txt file
            file_name = [S.Subj_id{i} '_' S.Sess_id{i} '_' S.Tract_type{i} '.txt'];
            file_path = fullfile(data_dir, 'no_correction', file_name);
            if isfile(file_path)
                C = readtable(file_path, 'Delimiter', '\t');
                T = struct('qa', {C.Var13});
                %T.Properties.VariableNames = {'x', 'y', 'z', 'dx0', 'dy0', 'dz0', 'dx1', 'dy1', 'dz1', 'dx2', 'dy2', 'dz2', 'qa', 'ICBM152_adult_T1W', 'ICBM152_adult_T2W', 'ICBM152_adult_WM'};
                T.Properties.VariableNames = {'qa'};
                %extract qa column
                if ismember('qa', T.Properties.VariableNames)
                    qa_values = T.qa;
                    % Calculate statistics
                    D.sn(i,1) = S.sn(i);
                    D.Subj_id{i,1} = S.Subj_id{i};
                    D.subj_nm(i,1) = S.subj_nm(i);
                    D.Group{i,1} = S.Group{i};
                    D.Sess_id{i,1} = S.Sess_id{i};
                    D.sess_nm(i,1) = S.sess_nm(i);
                    D.brain_side(i,1) = S.brain_side(i);
                    D.lesion(i,1) = S.lesion(i);
                    D.tract{i,1} = S.Tract_type{i};
                    D.dcst(i,1) = S.dcst(i);
                    D.icst(i,1) = S.icst(i);
                    D.rst(i,1) = S.rst(i);
                    D.meanQA(i,1) = mean(qa_values);
                    D.medianQA(i,1) = median(qa_values);
                    D.stdQA(i,1)= std(qa_values);
                    %keyboard;
                else 
                    warning('The "qa" column was not found in the file: %s', file_path);
                end
            else 
                warning('File does not exist: %s', file_path);
            end
            %alldat = addstruct(alldat);
        end 
            save(fullfile(analysis_dir, 'D.mat'), 'D');
            varargout = {D};
    case 'scatter_plot'
        if nargin < 2
            sn = (1:nsess);
        else 
            sn = varargin{1};
        end 
        D1   = load(fullfile(analysis_dir,'D.mat'));
        % Extracting data set for each tract from both hemisphere
        sn = unique(D1.D.Subj_id);
        extacted_data = struct();
        for i = 1:length(sn) 
            %OA data set for session A1 & A2
            DCST_L_OA_1 = D1.D.meanQA(strcmp(D1.D.Group, 'OA') & D1.D.sess_nm ==1 & D1.D.dcst==1 & D1.D.lesion == 0 & D1.D.brain_side ==1);
            DCST_R_OA_1 = D1.D.meanQA(strcmp(D1.D.Group, 'OA') & D1.D.sess_nm ==1 & D1.D.dcst==1 & D1.D.lesion == 0 & D1.D.brain_side ==2);
            ICST_L_OA_1 = D1.D.meanQA(strcmp(D1.D.Group, 'OA') & D1.D.sess_nm ==1 & D1.D.icst==1 & D1.D.lesion == 0 & D1.D.brain_side ==1);
            ICST_R_OA_1 = D1.D.meanQA(strcmp(D1.D.Group, 'OA') & D1.D.sess_nm ==1 & D1.D.icst==1 & D1.D.lesion == 0 & D1.D.brain_side ==2);
            RST_L_OA_1 = D1.D.meanQA(strcmp(D1.D.Group, 'OA') & D1.D.sess_nm ==1 & D1.D.rst==1 & D1.D.lesion == 0 & D1.D.brain_side ==1);
            RST_R_OA_1 = D1.D.meanQA(strcmp(D1.D.Group, 'OA') & D1.D.sess_nm ==1 & D1.D.rst==1 & D1.D.lesion == 0 & D1.D.brain_side ==2);
            
            %verify if A2 data exist or not 
            if any(strcmp(D1.D.sess_nm, 2))
                DCST_L_OA_2 = D1.D.meanQA(strcmp(D1.D.Group, 'OA') & D1.D.sess_nm ==2 & D1.D.dcst==1 & D1.D.lesion == 0 & D1.D.brain_side ==1);
                DCST_R_OA_2 = D1.D.meanQA(strcmp(D1.D.Group, 'OA') & D1.D.sess_nm ==2 & D1.D.dcst==1 & D1.D.lesion == 0 & D1.D.brain_side ==2);
                ICST_L_OA_2 = D1.D.meanQA(strcmp(D1.D.Group, 'OA') & D1.D.sess_nm ==2 & D1.D.icst==1 & D1.D.lesion == 0 & D1.D.brain_side ==1);
                ICST_R_OA_2 = D1.D.meanQA(strcmp(D1.D.Group, 'OA') & D1.D.sess_nm ==2 & D1.D.icst==1 & D1.D.lesion == 0 & D1.D.brain_side ==2);
                RST_L_OA_2 = D1.D.meanQA(strcmp(D1.D.Group, 'OA') & D1.D.sess_nm ==2 & D1.D.rst==1 & D1.D.lesion == 0 & D1.D.brain_side ==1);
                RST_R_OA_2 = D1.D.meanQA(strcmp(D1.D.Group, 'OA') & D1.D.sess_nm ==2 & D1.D.rst==1 & D1.D.lesion == 0 & D1.D.brain_side ==2);
            else 
                DCST_L_OA_2 = NaN;
                DCST_R_OA_2 = NaN;
                ICST_L_OA_2 = NaN;
                ICST_R_OA_2 = NaN;
                RST_L_OA_2 = NaN;
                RST_R_OA_2 = NaN;
                warning(['Session A2 data missing for Subject: ' sn{i} ]);
            end
        end 
        
        
         
       
        
end 
