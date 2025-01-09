#include<iostream>
using namespace std;


int T;
int R,C;


int main(){
    int i,j,k;
    cin>>T;
    for(int cas = 1; cas<=T ; ++cas){
        cin>>R>>C;
        int sum = 0;
        for(i=0;i<R;++i){
            for(j=0;j<C;++j){
                cin>>k;
                if((i+j)%2) sum += k;
                else sum -= k;
            }
        }
        if(sum==0) cout<<"0\n";
        else cout<<"1\n";
    }
    return 0;
}
