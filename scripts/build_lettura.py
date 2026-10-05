"""Extract the entire non-LESSON folklore unit; never truncate to headings.

Requires only the standard library. Does NOT change other apps or hub/cards.
Use integrate_lettura.py separately, after coordinating concurrent lesson edits.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/Users/it/.jaine/media/inbound/Copy_of_test---8746b41d-eb5a-4e13-a04e-8e0ca58130f5.docx')
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def strip_icon(s):
    m=re.search(r'[A-Za-zÀ-ÿ«“]',s)
    return s[m.start():].strip() if m else s.strip()

def paragraph_text(p):
    # Text runs alone discard Word's explicit in-paragraph line breaks.
    w='{'+NS['w']+'}'
    return ''.join((n.text or '') if n.tag==w+'t' else '\n' if n.tag==w+'br' else '\t' if n.tag==w+'tab' else '' for n in p.iter())

# Generated study responses, NOT an answer key quoted from the DOCX.
RESPONSES={
'Da dove deriva l’immagine moderna della strega?':('Where does the modern image of the witch come from?','Mainly from fairy tales and popular culture.'),
'Che cosa facevano molte donne considerate streghe?':('What did many women considered witches do?','They knew medicinal herbs, helped women give birth and prepared remedies; some were healers or midwives.'),
'Perché alcune persone le accusavano?':('Why did some people accuse them?','Fear and superstition led people to suspect magic or dealings with the devil.'),
'In quale periodo si svolsero molti processi?':('During what period did many trials take place?','Between the fifteenth and seventeenth centuries.'),
'Che cosa pensano oggi gli storici?':('What do historians think today?','Many accusations reflected fear, superstition and conflicts between neighbours rather than real evidence.'),
'Che cosa possiamo imparare studiando la stregoneria?':('What can we learn by studying witchcraft?','How people interpreted the world, and how fears and beliefs shaped past societies.'),
'Chi è la Befana?':('Who is the Befana?','An Italian folklore figure who brings sweets to well-behaved children and coal to those who misbehave, on the night of 5–6 January.'),
'Quali potrebbero essere le origini della Befana?':('What might the origins of the Befana be?','Possibly ancient, pre-Christian agricultural rituals connected with the end of winter and a new natural cycle.'),
'Dove vivevano, secondo la leggenda, le Janare?':('Where did the Janare live, according to the legend?','Around Benevento in Campania; they supposedly gathered near a large walnut tree.'),
'Chi erano le Masche?':('Who were the Masche?','Figures of Piedmontese folklore who could supposedly transform into animals; some helped people, others played tricks.'),
'Perché esistono tante versioni delle stesse leggende?':('Why are there so many versions of the same legends?','Stories were passed down orally; each village and family added new details.'),
'Quali animali compaiono spesso nelle storie di streghe?':('Which animals often appear in stories about witches?','Black cats, owls and wolves.'),
'In quali secoli si svolsero i processi alle streghe?':('In which centuries did witch trials take place?','Mainly between the fifteenth and seventeenth centuries.'),
'Chi veniva accusato più spesso?':('Who was accused most often?','Women, although some men were also tried.'),
'Quali situazioni potevano far nascere un’accusa?':('What situations could give rise to an accusation?','A quarrel between neighbours, sick livestock, a failed harvest or a reputation for knowing medicinal herbs.'),
'Perché gli storici non considerano affidabili molte confessioni?':('Why do historians consider many confessions unreliable?','Some were obtained under threats or torture, rather than freely given.'),
'Perché i processi diminuirono nel XVIII secolo?':('Why did trials decline in the eighteenth century?','Developments in science, medicine and more rational approaches weakened belief in witchcraft.'),
'Perché oggi si studia ancora questo periodo?':('Why is this period still studied today?','To understand how fear, superstition and social tensions influence communities.'),
'Che cos’è il malocchio?':('What is the evil eye?','A folk belief that an envious look can cause bad luck or illness; the reading presents it as a belief, not an established fact.'),
'A che cosa serve il cornicello?':('What is the cornicello used for?','Traditionally, the red horn amulet is supposed to protect against bad luck.'),
'Che cosa fanno alcune persone se cade il sale?':('What do some people do when salt is spilled?','They throw a pinch of salt over their left shoulder.'),
'Perché il numero 17 è considerato sfortunato?':('Why is the number 17 considered unlucky?','The reading links Roman XVII to VIXI, Latin for “I have lived”, interpreted as “my life is over”.'),
'Tutti gli italiani credono davvero a queste superstizioni?':('Do all Italians really believe in these superstitions?','No. The reading says most consider them traditions, followed for fun or “just in case”.'),
'Quale superstizione ti ha sorpreso di più?':('Which superstition surprised you most?',None),
'Dove si trovava il famoso noce?':('Where was the famous walnut tree?','Near Benevento, in Campania; its original exact location is uncertain.'),
'Che cosa raccontavano i contadini?':('What did the farmers report?','Strange lights, music and women dressed in white dancing around the tree.'),
'Che cosa facevano, secondo la leggenda, le streghe?':('What did the witches do, according to the legend?','They gathered at full moon, lit bonfires, sang and danced, then disappeared before dawn.'),
'Perché la storia cambiava nel corso dei secoli?':('Why did the story change over the centuries?','Each generation added new details.'),
'Quale popolo potrebbe aver dato origine alla leggenda?':('Which people might have given rise to the legend?','The Lombards and their possible sacred-tree rituals; the reading explicitly calls this an unconfirmed theory.'),
'Gli storici possono dimostrare che il sabba sia realmente esistito?':('Can historians prove that the witches’ gathering really existed?','No. The existence of the legend is documented, not the alleged supernatural events.'),
'Chi era Matteuccia?':('Who was Matteuccia?','Matteuccia di Francesco, a woman from Todi who knew medicinal herbs and prepared remedies; she was tried in 1428.'),
'Perché molte persone si rivolgevano a lei?':('Why did many people turn to her?','For remedies and help with illnesses, particularly when no doctor was nearby.'),
'Che cosa racconta la confessione?':('What does the confession describe?','An ointment, a magical formula and a supposed night flight on a he-goat to meet other witches; these are recorded allegations, not proven events.'),
'Perché gli storici non la considerano una prova affidabile?':('Why do historians not consider it reliable evidence?','Interrogations could involve pressure or torture, and confessions could repeat existing stories or suggestions.'),
'Che cosa ci insegna questo processo?':('What does this trial teach us?','How justice worked in the fifteenth century and what fears existed in society, not that magic existed.'),
'Perché il caso di Matteuccia è ancora studiato oggi?':('Why is Matteuccia’s case still studied today?','It is an early documented case, important for the history of trials, beliefs and the developing image of the witch.'),
'Perché alcune famiglie lasciavano una scopa davanti alla porta?':('Why did some families leave a broom at the door?','According to the legend, a Janara would have to count every broom bristle, delaying her until dawn.'),
'Che cosa raccontò il contadino dopo quella notte?':('What did the farmer say after that night?','That a Janara had entered his house: he reported a presence, inability to move or speak and a female figure.'),
'Quale rimedio consigliò il vicino alla donna anziana?':('What remedy did the neighbour suggest to the elderly woman?','To scatter a handful of salt in front of the door, supposedly forcing the Janara to count the grains.'),
'Che cos’è la paralisi del sonno?':('What is sleep paralysis?','In the reading, a state in which someone is conscious but briefly unable to move, sometimes with vivid hallucinations.'),
'Perché gli studiosi collegano questo fenomeno alle Janare?':('Why do researchers connect this phenomenon with the Janare?','The reported immobility, fear, sensed presence and dark figures resemble some sleep-paralysis experiences; this is an interpretation, not proof about each old account.'),
'Le Janare fanno ancora parte della cultura campana?':('Are the Janare still part of Campanian culture?','Yes: the reading mentions statues, festivals, books and local products, especially around Benevento.'),
'Pensi che nel passato le persone fossero più superstiziose di oggi?':('Do you think people in the past were more superstitious than people today?',None),
'Conosci qualche leggenda del tuo Paese?':('Do you know any legends from your country?',None),
'Perché la gente aveva paura delle streghe?':('Why were people afraid of witches?',None),
'Oggi esistono ancora superstizioni?':('Do superstitions still exist today?',None),
'Perché nascono le leggende?':('Why do legends arise?',None),
'Quale leggenda ti sembra più interessante?':('Which legend seems most interesting to you?',None),
'Nel tuo Paese esiste una figura simile alla Befana?':('Is there a figure similar to the Befana in your country?',None),
'Perché le persone inventano storie sul soprannaturale?':('Why do people invent stories about the supernatural?',None),
'Ti piace il folclore oppure preferisci la storia documentata?':('Do you enjoy folklore, or do you prefer documented history?',None),
'Perché pensi che la paura possa influenzare il giudizio delle persone?':('Why do you think fear can influence people’s judgment?',None),
'Conosci altri esempi storici in cui la paura ha portato ad accusare persone innocenti?':('Do you know other historical examples in which fear led to accusations against innocent people?',None),
'Perché è importante studiare la storia anche quando è difficile o ingiusta?':('Why is it important to study history even when it is difficult or unjust?',None),
'Pensi che oggi esistano ancora superstizioni diffuse?':('Do you think widespread superstitions still exist today?',None),
'Quali superstizioni esistono nel tuo Paese?':('What superstitions exist in your country?',None),
'Pensi che alcune superstizioni abbiano un’origine pratica?':('Do you think some superstitions have a practical origin?',None),
'Perché le tradizioni sopravvivono anche quando la società cambia?':('Why do traditions survive even when society changes?',None),
'C’è una superstizione che segui “per sicurezza”, anche se non ci credi?':('Is there a superstition you follow “just in case”, even though you do not believe in it?',None),
'Che cosa penseresti?':('What would you think?',None),
'Andresti a vedere?':('Would you go and look?',None),
'Avresti paura?':('Would you be afraid?',None),
'Oppure cercheresti una spiegazione razionale?':('Or would you look for a rational explanation?',None),
'Perché quasi tutte le culture hanno inventato figure simili?':('Why have almost all cultures invented similar figures?',None),
'Quali elementi hanno in comune?':('What elements do they have in common?',None),
'Quali sono le differenze?':('What are the differences?',None),
'Che cosa ci raccontano queste leggende sulle paure e sulle credenze delle diverse società?':('What do these legends tell us about the fears and beliefs of different societies?',None),
}

FACTS=[
('La formula attribuita a Matteuccia','«Unguento, unguento, mandami al noce di Benevento, sopra l’acqua e sopra il vento, e sopra ogni altro maltempo.»','Ointment, ointment, send me to the walnut tree of Benevento, above the water and above the wind, and above every other bad weather. The reading warns that the words may have been recorded under interrogation pressure.'),
('Guaritrice o strega?','Nel Medioevo il confine tra medicina popolare, superstizione e magia era spesso poco chiaro.','In the Middle Ages, the boundary between folk medicine, superstition and magic was often unclear. Some respected the women who made natural remedies; others feared them.'),
('Gli Strigoi','In Romania esistono gli Strigoi.','In Romanian folklore, spirits or people said to return after death, trouble families and bring disease or bad luck. The reading links these legends to the modern vampire myth.'),
('Lamia','Nell’antica Grecia si raccontava la storia di Lamia.','In the Greek myth presented here, a queen transformed into a monster; later versions describe her as a monster or sorceress who frightened children.'),
('Yamauba','Tra le montagne del Giappone vive, secondo il folclore, la Yamauba.','A woman of Japanese mountain folklore, portrayed as a dangerous monster in some stories and a helper of lost travellers in others.'),
('Le sorcières','In Francia le streghe vengono chiamate sorcières.','The French word for witches. The reading associates accusations in France with fear, superstition and social tensions.'),
('Baba Jaga','Una delle figure più famose del folclore slavo è Baba Jaga.','A Slavic folklore figure living in a hut on chicken legs and flying in a mortar with a pestle; she may help or test heroes, and may be cruel or wise.'),
('Le Hexen e la Notte di Valpurga','In Germania le streghe sono chiamate Hexen.','Hexen means witches in German. According to the tradition in the reading, they gather on the Brocken on 30 April, Walpurgis Night.'),
('Etimologia: strega','📚 La parola italiana strega deriva dal latino strix.','The reading traces Italian strega to Latin strix, a nocturnal bird associated with unsettling ancient stories.'),
('Etimologia: witch','🧙 L’inglese witch deriva dall’antico inglese wicce (forma femminile) e wicca (forma maschile).','The reading traces English witch to Old English wicce (feminine) and wicca (masculine).'),
('Etimologia: sorcière','🇫🇷 In francese sorcière deriva dal latino sortiarius, legato al destino e agli incantesimi.','The reading traces French sorcière to Latin sortiarius, connected with fate and spells.'),
('Etimologia: Hexe','🇩🇪 Il tedesco Hexe deriva da un’antica parola germanica che indicava una figura associata alla magia.','The reading traces German Hexe to an old Germanic word denoting a figure associated with magic; it does not supply that older word.'),
]

# In document order, per source section. Answers are derived from that reading.
TRUE_FALSE={
2:[False,True,True,False,True,True],
3:[False,True,False,True,True,True],
4:[False,True,False,True,False,True],
5:[False,True,False,True,False,True],
7:[False,True,True,False,True,False],
8:[True,True,False,True,False,True],
9:[False,True,True,True,False,True],
}

def extract():
    with ZipFile(SOURCE) as z: xml=ET.fromstring(z.read('word/document.xml'))
    paragraphs=[paragraph_text(p) for p in xml.findall('.//w:body//w:p',NS)]
    start=paragraphs.index('🧙 Folclore Italiano')
    boundaries=[start]+[i for i in range(start+1,len(paragraphs)) if paragraphs[i] in ('🧙 Folclore Italiano','📚 Le Grandi Leggende delle Streghe Italiane','🧙 Le Grandi Leggende delle Streghe Italiane','🧙 Le Grandi Leggende delle Streghe')]
    boundaries.append(len(paragraphs))
    sections=[];cards=[]
    def card(section,kind,it,other,paragraph,**extra):
        c=dict(it=it,other=other,lang='EN',group='Liam · Lettura',tags=['liam','lettura'],kind=kind,reading=section['id'],sourceParagraph=paragraph,note=f"Liam · Lettura · {section['title']} · DOCX paragraph {paragraph+1}",**extra)
        cards.append(c);return c
    for number,(a,b) in enumerate(zip(boundaries,boundaries[1:]),1):
        part=next((t for t in paragraphs[a:b] if t.startswith('Parte ')),None)
        title=part or 'Le Grandi Leggende · programma completo'
        if a==6354: title+=' · versione annotata'
        section=dict(id=f'lettura-{number:02}',title=title,startParagraph=a,endParagraph=b-1,paragraphs=[dict(index=i,text=paragraphs[i]) for i in range(a,b)],questions=[])
        sections.append(section)
        source='\n'.join(paragraphs[a:b])
        card(section,'reading',title,'Read the complete original passage, including its historical cautions, vocabulary and exercises. Then answer its questions in Italian. This is a reading task, not an English translation of the passage.',a,sourceText=source)
        mode=None
        for i in range(a,b):
            t=paragraphs[i].strip();clean=strip_icon(t)
            if t.startswith('💬 Hai capito?'):mode='comprehension';continue
            if t.startswith('🗣️ Parliamone'):mode='discussion';continue
            if t=='Domande:':mode='discussion';continue
            if t.startswith(('✍️ Scrittura',)):mode='writing';continue
            if t and not re.match(r'^[A-Za-zÀ-ÿ«“•]',t) and not t.startswith(('• ',)):
                mode=None
            # Never infer answers for open questions. Occurrences remain distinct.
            if '?' in t and clean in RESPONSES and mode in ('comprehension','discussion','writing'):
                en,answer=RESPONSES[clean]
                q=dict(prompt=t,translation=en,answer=answer,type='open' if answer is None else 'comprehension',sourceParagraph=i)
                section['questions'].append(q)
                other=en+'\n\n'+('Suggested response based on the reading: '+answer if answer else 'Open response: give your own answer in Italian. There is no single correct answer.')
                card(section,q['type'],t,other,i)
            if ' = ' in t:
                it,en=t.split(' = ',1)
                card(section,'vocabulary',strip_icon(it),en.strip(),i)
        # Keep all true/false statements and complete grammar tasks, not only
        # questions ending in '?' or those underneath a LESSON heading.
        for i in range(a,b):
            heading=paragraphs[i].strip()
            if heading.startswith('✅ Vero o falso?'):
                statements=[]
                j=i+1
                while j<b and (not paragraphs[j].strip() or re.match(r'^[A-Za-zÀ-ÿ]',paragraphs[j])):
                    if paragraphs[j].strip(): statements.append((j,paragraphs[j]))
                    j+=1
                answers=TRUE_FALSE[number]
                assert len(statements)==len(answers),(number,statements)
                for (j,prompt),answer in zip(statements,answers):
                    response='According to the reading: '+('True (vero).' if answer else 'False (falso).')
                    section['questions'].append(dict(prompt=prompt,translation='True or false? Justify your answer using the passage.',answer=response,type='truefalse',sourceParagraph=j))
                    card(section,'truefalse',prompt,response,j)
            if heading.startswith(('📚 Ripassiamo la grammatica','🔄 Ripasso','🔄 Trasforma')):
                j=i+1
                while j<b:
                    text=paragraphs[j].strip()
                    # Exercise arrows are part of a transformation task.
                    if text and not re.match(r'^[A-Za-zÀ-ÿ«“/]',text) and not text.startswith('➡️'):break
                    j+=1
                task='\n'.join(paragraphs[i:j])
                card(section,'exercise',task,'Complete the original grammar or tense-transformation task in Italian. The full source task, including its options and any learner annotations, is preserved on the front. Check the tense and subject agreement; no original answer key is supplied for this task.',i)
    for title,needle,en in FACTS:
        i=paragraphs.index(needle,start)
        section=next(s for s in sections if s['startParagraph']<=i<=s['endParagraph'])
        card(section,'source-fact',title,en,i,sourceExcerpt=needle)
    assert [p['text'] for s in sections for p in s['paragraphs']]==paragraphs[start:]
    return dict(owner='Liam',title='Le streghe: lettura integrale',source=dict(filename=SOURCE.name,sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),startParagraph=start,paragraphCount=len(paragraphs)-start,extraction='Every body paragraph, including tables, in document order. Zero-based source indices.',answerPolicy='Suggested study responses generated from the reading, not an original answer key. Historical statements remain attributed to the source.'),sections=sections,cards=cards)

if __name__=='__main__':
    d=extract()
    (ROOT/'liam-lettura.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    template=(ROOT/'scripts/lettura-template.html').read_text()
    payload=json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    (ROOT/'liam-lettura.html').write_text(template.replace('__READING_DATA__',payload))
    print(json.dumps(dict(sections=len(d['sections']),paragraphs=d['source']['paragraphCount'],questions=sum(len(s['questions']) for s in d['sections']),cards=len(d['cards'])),indent=2))
