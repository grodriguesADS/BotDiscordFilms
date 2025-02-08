import discord
from sqlalchemy.orm import sessionmaker
from data.db_setup import engine, Filme
import requests
from config.config import TMDB_API_KEY
from datetime import datetime, timedelta

Session = sessionmaker(bind=engine)
session = Session()

def setup(bot):
    @bot.command()
    async def addfilme(ctx, *, filme: str):
        filme = filme.strip()  
  
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={filme}&language=pt-BR"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results:
                  
                    movie = results[0]
                    movie_id = movie.get('id')
                    title_pt = movie.get('title')
                    title_original = movie.get('original_title')
                    release_date = movie.get('release_date')
                    rating = movie.get('vote_average')
                    poster_path = movie.get('poster_path')

                 
                    existe_filme = session.query(Filme).filter(
                        (Filme.filme == title_pt) | (Filme.titulo_original == title_original)
                    ).first()

                    if existe_filme:
                        await ctx.send(f'O filme "{title_pt}" já existe na lista.')
                    else:
                     
                        formatted_date = "Data não disponível"
                        if release_date:
                            formatted_date = datetime.strptime(release_date, '%Y-%m-%d').strftime('%d/%m/%Y')
                        
                     
                        movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=pt-BR"
                        details_response = requests.get(movie_details_url, timeout=5)
                        
                        if details_response.status_code == 200:
                            details_data = details_response.json()
                            duration = details_data.get('runtime') 
                        else:
                            duration = None
                        
                    
                        novo_filme = Filme(
                            filme=title_pt,
                            titulo_original=title_original,
                            data_lancamento=formatted_date,
                            avaliacao=rating,
                            duracao=duration,
                            imagem=poster_path
                        )
                        
                  
                        session.add(novo_filme)
                        session.commit()
                        
                 
                        await ctx.send(f'Filme adicionado: {title_pt}')
                        
                    
                        movie_info = (
                            f"Título: {title_pt}\n"
                            f"Título Original: {title_original}\n"
                            f"Lançamento: {formatted_date}\n"
                            f"Avaliação: {rating}/10\n"
                            f"Duração: {duration} minutos" if duration else "Duração não disponível\n"
                        )
                        await ctx.send(f"```\n{movie_info}\n```")
                        
               
                        if poster_path:
                            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                            await ctx.send(poster_url)
                else:
                    await ctx.send("Nenhum filme encontrado com esse título.")
            elif response.status_code == 401:
                await ctx.send("Erro 401: Não autorizado. Verifique sua chave da API TMDB.")
            else:
                error_message = f"Ocorreu um erro ao acessar a API do TMDB: {response.status_code} - {response.reason}"
                await ctx.send(error_message)
        
        except requests.Timeout:
            await ctx.send("A busca demorou demais e não foi possível obter os dados.")
        except requests.RequestException as e:
            await ctx.send(f"Ocorreu um erro ao acessar a API do TMDB: {str(e)}")

    @bot.command()
    async def listafilmes(ctx):
    
        filmes = session.query(Filme).all()
        
        if filmes:
        
            for filme in filmes:
            
                movie_info = (
                    f"**Título:** {filme.filme}\n"
                    f"**Título Original:** {filme.titulo_original}\n"
                    f"**Lançamento:** {filme.data_lancamento}\n"
                    f"**Avaliação:** {filme.avaliacao}/10\n"
                    f"Duração: {filme.duracao} minutos\n"
                )
                
        
                await ctx.send(movie_info)
                
            
                if filme.imagem:
                    poster_url = f"https://image.tmdb.org/t/p/w500{filme.imagem}"
                    await ctx.send(poster_url)  
                
            
                await ctx.send("---------------")
        else:
            await ctx.send("A lista está vazia.")


    @bot.command()
    async def removefilme(ctx, *, filme: str):
        filme = filme.strip()
        existe_filme = session.query(Filme).filter_by(filme=filme).first()

        if existe_filme:
            session.delete(existe_filme)
            session.commit()  
            await ctx.send(f'Filme removido: {filme}')
        else:
            await ctx.send(f'Filme não encontrado: {filme}')

            
    @bot.command()
    async def procurafilme(ctx, *, query: str):
        query = query.strip()
        
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language=pt-BR"
        
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results:
                
                    results = sorted(results, key=lambda x: x['popularity'], reverse=True)
                
                    filmes_relevantes = [movie for movie in results if query.lower() in movie['title'].lower() or query.lower() in movie['original_title'].lower()]
                
                if filmes_relevantes:
                    await ctx.send("**Filmes encontrados:**")
                    for movie in filmes_relevantes[:5]:
                        movie_id = movie.get('id')
                        title_pt = movie.get('title')  
                        title_original = movie.get('original_title')  
                        release_date = movie.get('release_date')  
                        rating = movie.get('vote_average')  
                        poster_path = movie.get('poster_path')
                        
                        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=pt-BR"
                        details_response = requests.get(details_url, timeout=5)
                    
                    if details_response.status_code == 200:
                        movie_details = details_response.json()
                        runtime = movie_details.get('runtime') 
                    else:
                        runtime = None
                        
                        if release_date:
                            release_date_obj = datetime.strptime(release_date, '%Y-%m-%d')
                            formatted_date = release_date_obj.strftime('%d/%m/%Y')
                        else:
                            formatted_date = "Data não disponível"
                
                        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                        
                    
                        movie_info = (
                            f"Título: {title_pt}\n"
                            f"Título Original: {title_original}\n"
                            f"Data de Lançamento: {formatted_date}\n"
                            f"Avaliação: {rating}/10"
                            f"Duração: {runtime} minutos" if runtime else "Duração não disponível\n"
                        )
            
                        await ctx.send(f"```\n{movie_info}\n```")
                        
                        
                        if poster_url:
                            await ctx.send(poster_url)
                            
                        await ctx.send("\n" + "-" * 30 + "\n")
                
                else:
                    await ctx.send("Nenhum filme encontrado.")
            elif response.status_code == 401:
                await ctx.send("Erro 401: Não autorizado. Verifique sua chave da API TMDB.")
            else:
                error_message = f"Ocorreu um erro ao acessar a API do TMDB: {response.status_code} - {response.reason}"
                await ctx.send(error_message)
        
        except requests.Timeout:
            await ctx.send("A busca demorou demais e não foi possível obter os dados.")
        except requests.RequestException as e:
            await ctx.send(f"Ocorreu um erro ao acessar a API do TMDB: {str(e)}")
            
    @bot.command()
    async def geraarquivo(ctx):
        filmes = session.query(Filme).all()  
        
        if filmes:
        
            conteudo_arquivo = "\n".join([filme.titulo_original for filme in filmes])
            
            nome_arquivo = "data/files/filmes_indicados.txt"
            
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo_arquivo)
        
            await ctx.send("Aqui está o arquivo com os títulos originais dos filmes:", file= discord.File(nome_arquivo))
        else:
            await ctx.send("Não há filmes no banco de dados.")
            
    @bot.command()
    async def temporestante(ctx, *, filme: str):
        filme = filme.strip()

        filme_encontrado = session.query(Filme).filter(
            (Filme.filme == filme) | (Filme.titulo_original == filme)
        ).first()

        if not filme_encontrado:
            await ctx.send(f'Filme "{filme}" não encontrado na lista.')
            return

     
        if filme_encontrado.duracao is None:
            await ctx.send(f'O filme "{filme_encontrado.filme}" não tem uma duração registrada.')
            return

       
        duracao_minutos = filme_encontrado.duracao
        hora_atual = datetime.now()

     
        hora_termino = hora_atual + timedelta(minutes=duracao_minutos)

       
        hora_atual_str = hora_atual.strftime('%H:%M')
        hora_termino_str = hora_termino.strftime('%H:%M')

      
        await ctx.send(
            f"Se começar o filme: '{filme_encontrado.filme}' agora {hora_atual_str}.\n "
            f"O filme vai terminar às {hora_termino_str}.\n Aproveite!"
        )

            
    @bot.command()
    async def helpdb(ctx):
        help_message = (
            "Aqui estão os comandos disponíveis:\n"
            "`db!addfilme <nome do filme>` - Adiciona um filme à lista.\n"
            "`db!removefilme <nome do filme>` - Remove um filme da lista.\n"
            "`db!listafilmes` - Exibe todos os filmes na lista.\n"
            "`db!procurafilme <nome do filme>` - Procura um filme na TMDB.\n"
            "`db!geraarquivo` - Gera lista dos filmes na lista.\n"
            "`db!temporestante` - Informa que horas o filme acaba.\n"
            "`db!helpdb` - Mostra esta mensagem de ajuda."
        )
        await ctx.send(help_message)