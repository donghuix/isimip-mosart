clear;close all;clc;

% ####################################################################### %
% Description: read station information from GSIM metadata and find the 
%              corresponding station number in the dataset
%
% Download data from https://doi.pangaea.de/10.1594/PANGAEA.887477
%
% Author: Donghui Xu
% Date: 08/12/2020
% ####################################################################### %
clear;close all;clc

addpath('/Users/xudo627/Developments/Setup-E3SM-Mac/matlab-scripts-for-mosart/');
filename = '../data/GSIM_metadata/GSIM_catalog/GSIM_metadata.csv';
load coastlines.mat

fid = fopen(filename);
k = 0;
while ~feof(fid) % feof(fid) is true when the file ends
      tline = fgetl(fid);
      s = strsplit(tline,',');
      if ( k > 0 )
          gsim_no{k} = s{1};
          agent{k} = s{2};
          tmpstr = s{8};
          river{k} = tmpstr(2:end-1); % remove quotation marks
          if length(s) == 30
              lat(k) = str2double(s{14});
              lon(k) = str2double(s{15});
              area(k)= str2double(s{17});
          elseif length(s) == 29
              lat(k) = str2double(s{13});
              lon(k) = str2double(s{14});
              area(k)= str2double(s{16});
          elseif length(s) == 28
              lat(k) = str2double(s{12});
              lon(k) = str2double(s{13});
              area(k)= str2double(s{15});
          elseif length(s) == 27 
              lat(k) = str2double(s{11});
              lon(k) = str2double(s{12});
              area(k)= str2double(s{14});
          end

          if ( k > 1 )
            assert(~isnan(lat(k)) && ~isnan(lon(k)));
          end

          frac_missing_days(k) = str2double(s{24});
          year_start(k) = str2double(s{25});
          year_end(k)   = str2double(s{26});
      end
      k = k + 1;
end
s = strsplit(tline,',');
fclose(fid);

[B,I] = sort(area,'descend'); % area in km^2
ind = find(~isnan(B));
I = I(ind); B = B(ind);
fname = '/Users/xudo627/Library/CloudStorage/OneDrive-PNNL/projects/cesm-inputdata/rof/mosart/MOSART_global_half_20180721a.nc';
%fname = '/Users/xudo627/Library/CloudStorage/OneDrive-PNNL/projects/cesm-inputdata/rof/mosart/MOSART_Global_half_20200720.nc';
area_grid = ncread(fname,'area');
figure;
N = 1000;
area_mosart = NaN(N,1);
area_gsim   = NaN(N,1);
avail_years = NaN(N,1);
lon_gsim    = NaN(N,1);
lat_gsim    = NaN(N,1);
ioutlets    = NaN(N,1);
gsim_nos    = cell(N,1);
k = 0;

fid = fopen( 'gsim_index.csv', 'w' );
for i = 1 : N
    S = shaperead(['../data/GSIM_metadata/GSIM_catchments/' gsim_no{I(i)}(2:end-1) '.shp']);
    
    [ioutlet, icontributing] = find_mosart_cell(fname,lon(I(i)),lat(I(i)),area(I(i)).*1e6);
    error = (nansum(area_grid([ioutlet; icontributing])) - area(I(i)).*1e6)./(area(I(i)).*1e6) .* 100;
    
    if error <= 20 && error >= -20
        plot(S.X,S.Y,'k-','LineWidth',2); hold on;
        k = k + 1;
        area_mosart(k) = nansum(area_grid([ioutlet; icontributing]));
        area_gsim(k)   = area(I(i)).*1e6;
        avail_years(k) = year_end(I(i)) - year_start(I(i)) + 1;
        ioutlets(k)    = ioutlet;
        lon_gsim(k)    = lon(I(i));
        lat_gsim(k)    = lat(I(i));
        gsim_nos{k}    = gsim_no{I(i)}(2:end-1);
        [row,col]      = ind2sub([720 360],ioutlets(k));
        fprintf( fid, '%s,%.3f,%.3f,%.3f,%d,%d,%.3f\n', gsim_nos{k}, lon_gsim(k), lat_gsim(k), area_gsim(k), row-1, col-1, area_mosart(k));
        str = ['No. ' num2str(k) ', ' gsim_nos{k} ': Actual area = ' num2str(area(I(i))) ' [km^{2}], MOSART area = ' num2str(area_mosart(k)./1e6) ' [km^{2}]'];
        disp(str);
    end
end

plot(lon_gsim,lat_gsim,'r.','LineWidth',2); hold on; grid on;

figure;
loglog(area_gsim./1e6,area_mosart./1e6,'bx','LineWidth',2); hold on; grid on;
a = min([area_gsim; area_mosart]);
b = max([area_gsim; area_mosart]);
plot([a b]./1e6,[a b]./1e6,'r-','LineWidth',2);
xlabel('Station contributing area [km^{2}]','FontSize',15,'FontWeight','bold');
ylabel('MOSART contributing area [km^{2}]','FontSize',15,'FontWeight','bold');
